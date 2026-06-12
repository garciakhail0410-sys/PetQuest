import pygame
import pygame.gfxdraw
import sys
import os
import math
import random

pygame.init()

# ── Audio ─────────────────────────────────────────────────────────────────────
pygame.mixer.init()

def load_sound(filename):
    if os.path.exists(filename):
        return pygame.mixer.Sound(filename)
    return None

def play_sound(sound):
    if sound:
        sound.play()

pygame.mixer.music.load("landing.mp3") if os.path.exists("landing.mp3") else None
pygame.mixer.music.set_volume(0.3)
if os.path.exists("landing.mp3"):
    pygame.mixer.music.play(loops=-1)

# ── Sound effects ─────────────────────────────────────────────────────────────
sfx_click         = load_sound("click.mp3")
sfx_task_complete = load_sound("task_complete.wav")
sfx_lose          = load_sound("lose.mp3")
sfx_warning       = load_sound("warning.wav")
sfx_ambience      = load_sound("classroom_ambience.wav")
sfx_task_music    = load_sound("task.mp3")

AMBIENCE_CHANNEL  = pygame.mixer.Channel(0)
WARNING_CHANNEL   = pygame.mixer.Channel(1)
TASK_CHANNEL      = pygame.mixer.Channel(2)
CLICK_CHANNEL     = pygame.mixer.Channel(3)

warning_sound_playing = False
task_music_playing    = False

def play_sound(sound):
    if sound and not is_muted:
        CLICK_CHANNEL.stop()
        CLICK_CHANNEL.set_volume(vol_sfx)
        CLICK_CHANNEL.play(sound)

def start_classroom_ambience():
    if sfx_ambience:
        AMBIENCE_CHANNEL.play(sfx_ambience, loops=-1)
        AMBIENCE_CHANNEL.set_volume(vol_ambience)

def stop_classroom_ambience():
    AMBIENCE_CHANNEL.stop()

def play_warning_sound():
    global warning_sound_playing
    if sfx_warning and not warning_sound_playing:
        WARNING_CHANNEL.play(sfx_warning, loops=-1)
        WARNING_CHANNEL.set_volume(0.5)
        warning_sound_playing = True

def stop_warning_sound():
    global warning_sound_playing
    if warning_sound_playing:
        WARNING_CHANNEL.stop()
        warning_sound_playing = False

def start_task_music():
    global task_music_playing
    if sfx_task_music and not task_music_playing:
        TASK_CHANNEL.play(sfx_task_music, loops=-1)
        TASK_CHANNEL.set_volume(0.5)
        task_music_playing = True

def stop_task_music():
    global task_music_playing
    if task_music_playing:
        TASK_CHANNEL.stop()
        task_music_playing = False

# ── Mute toggle ───────────────────────────────────────────────────────────────

def draw_mute_button(surf):
    if sound_btn_img:
        alpha = 120 if is_muted else 255
        img = sound_btn_img.copy()
        img.set_alpha(alpha)
        surf.blit(img, (MUTE_RECT.x, MUTE_RECT.y))
    else:
        hov = MUTE_RECT.collidepoint(*pygame.mouse.get_pos())
        bg  = (110, 80, 45) if hov else (80, 55, 30)
        pygame.draw.rect(surf, bg, MUTE_RECT, border_radius=8)
        pygame.draw.rect(surf, (180, 140, 60), MUTE_RECT, 2, border_radius=8)
        symbol = "M" if is_muted else "S"
        lbl = font_small.render(symbol, True, WHITE)
        surf.blit(lbl, (MUTE_RECT.centerx - lbl.get_width() // 2,
                        MUTE_RECT.centery - lbl.get_height() // 2))

def draw_sound_popup(surf, anim_t):
    global sound_dragging_slider, vol_music, vol_sfx, vol_ambience
    if anim_t <= 0:
        return {}
    num_sliders = 2
    PW = 244
    PH = 36 + num_sliders * 48 + 34  # start_y + rows + mute button space
    scale  = 0.5 + 0.5 * min(anim_t, 1.0)
    pw_s   = int(PW * scale)
    ph_s   = int(PH * scale)
    px_s   = SCREEN_W - pw_s - 8
    py_s   = MUTE_RECT.bottom + 6

    panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.rect(panel, (28, 22, 48, 248), (0, 0, PW, PH), border_radius=14)
    pygame.draw.rect(panel, (120, 90, 180, 255), (0, 0, PW, PH), 2, border_radius=14)
    pygame.draw.rect(panel, (45, 30, 80, 240), (0, 0, PW, 28), border_radius=14)
    pygame.draw.rect(panel, (45, 30, 80, 240), (0, 14, PW, 14))
    t_lbl = font_small.render("VOLUME", True, (200, 175, 235))
    panel.blit(t_lbl, (PW // 2 - t_lbl.get_width() // 2, 7))

    sliders = [
        ("Game Sound",    vol_music,    "music"),
        ("Button Clicks", vol_sfx,      "sfx"),
    ]

    bar_x   = 14
    bar_w   = PW - 88
    bar_h   = 12
    start_y = 36
    row_gap = 48

    mx_now, my_now = pygame.mouse.get_pos()
    local_mx = (mx_now - px_s) / max(0.001, scale)
    local_my = (my_now - py_s) / max(0.001, scale)

    # apply active drag live
    if sound_dragging_slider in ("music", "sfx", "ambience"):
        if False:
            pass
        else:
            raw = max(0.0, min(1.0, (local_mx - bar_x) / max(1, bar_w)))
            if sound_dragging_slider == "music":
                vol_music = raw
                if not is_muted:
                    pygame.mixer.music.set_volume(raw)
                    TASK_CHANNEL.set_volume(raw * 0.5)
            elif sound_dragging_slider == "sfx":
                vol_sfx = raw
                if not is_muted:
                    CLICK_CHANNEL.set_volume(raw)
                    WARNING_CHANNEL.set_volume(raw * 0.5)
            elif sound_dragging_slider == "ambience":
                vol_ambience = raw
                if not is_muted:
                    AMBIENCE_CHANNEL.set_volume(raw)

    for si, (label, val, key) in enumerate(sliders):
        by  = start_y + si * row_gap
        by2 = by + 16

        is_locked = False
        lbl_col = (130, 110, 160) if is_locked else (200, 175, 235)
        lbl_s = font_ft_hint.render(label, True, lbl_col)
        panel.blit(lbl_s, (bar_x, by))

        if is_locked:
            lock_s = font_ft_hint.render("(in classroom only)", True, (110, 90, 140))
            panel.blit(lock_s, (bar_x + bar_w - lock_s.get_width() + 10, by))

        pygame.draw.rect(panel, (18, 13, 32), (bar_x, by2, bar_w, bar_h), border_radius=6)
        fill_w = max(0, int(bar_w * val))
        if fill_w > 0:
            if is_locked:
                fill_col = (70, 55, 100)
            elif sound_dragging_slider == key:
                fill_col = (160, 110, 240)
            else:
                fill_col = (130, 90, 210)
            pygame.draw.rect(panel, fill_col, (bar_x, by2, fill_w, bar_h), border_radius=6)
        pygame.draw.rect(panel, (100, 75, 160), (bar_x, by2, bar_w, bar_h), 1, border_radius=6)

        kx = bar_x + fill_w
        ky = by2 + bar_h // 2
        knob_col = (130, 110, 160, 180) if is_locked else (
            (240, 210, 255, 240) if sound_dragging_slider == key else (210, 185, 255, 220)
        )
        pygame.gfxdraw.filled_circle(panel, kx, ky, 9, knob_col)
        pygame.gfxdraw.aacircle(panel, kx, ky, 9, (160, 130, 220, 255))

        pct_col = (110, 90, 140) if is_locked else (180, 155, 220)
        pct = font_ft_hint.render(f"{int(val*100)}%", True, pct_col)
        panel.blit(pct, (bar_x + bar_w + 6, by2 + bar_h // 2 - pct.get_height() // 2))

    # Mute toggle button
    mut_y = start_y + len(sliders) * row_gap + 4
    mut_w = PW - 28
    mut_h = 24
    mut_hov = pygame.Rect(bar_x, mut_y, mut_w, mut_h).collidepoint(local_mx, local_my)
    mut_col = (200, 60, 60) if is_muted else ((90, 160, 70) if mut_hov else (55, 120, 45))
    pygame.draw.rect(panel, (0, 0, 0, 60), (bar_x + 2, mut_y + 3, mut_w, mut_h), border_radius=7)
    pygame.draw.rect(panel, mut_col, (bar_x, mut_y, mut_w, mut_h), border_radius=7)
    mut_txt = font_ft_hint.render(
        "X  MUTED  (click to unmute)" if is_muted else "Mute All",
        True, WHITE
    )
    panel.blit(mut_txt, (PW // 2 - mut_txt.get_width() // 2,
                          mut_y + mut_h // 2 - mut_txt.get_height() // 2))

    scaled = pygame.transform.smoothscale(panel, (pw_s, ph_s))
    surf.blit(scaled, (px_s, py_s))

    # return screen-space rects for hit-testing
    rects = {"panel": pygame.Rect(px_s, py_s, pw_s, ph_s)}
    for si, (label, val, key) in enumerate(sliders):
        by2 = start_y + si * row_gap + 16
        rects[key] = pygame.Rect(
            px_s + int(bar_x * scale),
            py_s + int(by2   * scale),
            int(bar_w         * scale),
            int((bar_h + 14)  * scale),
        )
    rects["mute"] = pygame.Rect(
        px_s + int(bar_x  * scale),
        py_s + int(mut_y  * scale),
        int(mut_w          * scale),
        int(mut_h          * scale),
    )
    return rects

_sound_popup_rects = {}

def toggle_sound_popup():
    global show_sound_popup, sound_popup_anim
    show_sound_popup = not show_sound_popup
    if not show_sound_popup:
        sound_popup_anim = 0.0

def toggle_mute():
    global is_muted, vol_music, vol_sfx, vol_ambience, _pre_mute
    is_muted = not is_muted
    if is_muted:
        _pre_mute = (vol_music, vol_sfx, vol_ambience)
        pygame.mixer.music.set_volume(0)
        AMBIENCE_CHANNEL.set_volume(0)
        WARNING_CHANNEL.set_volume(0)
        TASK_CHANNEL.set_volume(0)
        CLICK_CHANNEL.set_volume(0)
    else:
        vol_music, vol_sfx, vol_ambience = _pre_mute
        pygame.mixer.music.set_volume(vol_music)
        AMBIENCE_CHANNEL.set_volume(vol_ambience)
        WARNING_CHANNEL.set_volume(vol_sfx * 0.5)
        TASK_CHANNEL.set_volume(vol_music * 0.5)
        CLICK_CHANNEL.set_volume(vol_sfx)

SCREEN_W = 900
SCREEN_H = 510

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("PetQuest: Secret Paws")
clock = pygame.time.Clock()

# ── Sound button image ────────────────────────────────────────────────────────
SOUND_BTN_SIZE = 40
if os.path.exists("soundbutton.png"):
    _raw_snd_btn = pygame.image.load("soundbutton.png").convert_alpha()
    sound_btn_img = pygame.transform.smoothscale(_raw_snd_btn, (SOUND_BTN_SIZE, SOUND_BTN_SIZE))
else:
    sound_btn_img = None

# ── Colors ────────────────────────────────────────────────────────────────────
WHITE = (255, 255, 255)

BTN_GREEN  = (60,  195, 75);  BTN_GREEN_H  = (80,  220, 95);  BTN_GREEN_D  = (35,  140, 50)
BTN_BLUE   = (55,  155, 240); BTN_BLUE_H   = (80,  180, 255); BTN_BLUE_D   = (30,  105, 185)
BTN_YELLOW = (250, 195, 35);  BTN_YELLOW_H = (255, 215, 65);  BTN_YELLOW_D = (195, 145, 10)

PARCHMENT    = (245, 230, 195)
PARCHMENT_D  = (220, 200, 155)
WOOD_BROWN   = (139, 90,  43)
WOOD_DARK    = (100, 60,  20)
PLAY_GREEN   = (80,  175, 60)
PLAY_GREEN_H = (100, 205, 75)
PLAY_GREEN_D = (45,  120, 30)
CLOSE_RED    = (210, 60,  45)
CLOSE_RED_H  = (240, 85,  65)
CLOSE_RED_D  = (150, 35,  20)
WARN_ORANGE  = (220, 100, 30)
GOLD         = (210, 170, 40)
GOLD_LIGHT   = (255, 220, 80)

FT_BAR_BG     = ( 50,  30,  10)
FT_BAR_FILL_A = (255, 180,  30)
FT_BAR_FILL_B = (255, 120,   0)
FT_GREEN      = ( 80, 200,  70)

FT_DRAG_WOBBLE_STRENGTH = 14
FT_WOBBLE_FREQ          = 8.0
FT_SNAP_RADIUS          = 70
FT_DROP_PER_DRAG        = 0.34
FT_DRIFT_SPEED          = 220

# ── Water Task Colors ─────────────────────────────────────────────────────────
WT_BAR_BG     = (20,  50,  80)
WT_BAR_FILL_A = (80,  190, 255)
WT_BAR_FILL_B = (30,  120, 220)
WT_WATER_BLUE = (60,  160, 240)
WT_BOWL_RIM   = (180, 140,  80)
WT_WATER_DARK = (30,  100, 190)

# ── Whack-a-Mole Task Colors ──────────────────────────────────────────────────
WM_BG         = (60,  40,  20)
WM_PANEL_BG   = (80,  55,  25)
WM_BANNER     = (50,  30,  10)
WM_HOLE_COL   = (30,  18,   8)
WM_HOLE_RIM   = (100, 65,  25)
WM_TOY_COL    = (220, 80,  60)
WM_TOY_LIT    = (255, 130, 100)
WM_PROGRESS_A = (255, 180,  30)
WM_PROGRESS_B = (255, 120,   0)

# ── Simon Says Task Colors ────────────────────────────────────────────────────
SS_BG          = (55,  35,  75)
SS_PANEL_BG    = (70,  45,  95)
SS_BANNER      = (45,  25,  65)
SS_BTN_UP      = (100, 180, 255)
SS_BTN_DOWN    = (255, 130, 80)
SS_BTN_LEFT    = (100, 210, 130)
SS_BTN_RIGHT   = (255, 200, 60)
SS_BTN_LIT_UP      = (180, 230, 255)
SS_BTN_LIT_DOWN    = (255, 200, 150)
SS_BTN_LIT_LEFT    = (180, 255, 200)
SS_BTN_LIT_RIGHT   = (255, 240, 140)
SS_BTN_DARK    = (30,  20,  45)
SS_NOISE_BG    = (40,  15,  15)
SS_NOISE_FILL  = (220, 60,  40)
SS_NOISE_SAFE  = (80,  200, 70)
SS_PROGRESS_BG = (30,  20,  50)
SS_PROGRESS_FILL_A = (180, 100, 255)
SS_PROGRESS_FILL_B = (100, 60,  200)

# ── Cleanup Task Colors ───────────────────────────────────────────────────────
CL_BG          = (35,  55,  30)
CL_BANNER      = (25,  40,  20)
CL_FLOOR       = (190, 165, 120)
CL_FLOOR_DARK  = (160, 135,  90)
CL_DIRT_COL    = (130,  90,  45)
CL_DIRT_DARK   = ( 90,  60,  20)
CL_BROOM_HDL   = (180, 120,  50)
CL_BROOM_HEAD  = (220, 190, 100)
CL_SPARKLE     = (255, 240, 100)
CL_PROGRESS_A  = (120, 220,  80)
CL_PROGRESS_B  = ( 60, 160,  40)

# ── Volume settings ───────────────────────────────────────────────────────────
vol_music    = 0.3
vol_sfx      = 1.0
vol_ambience = 0.4
is_muted = False
_pre_mute = (0.3, 1.0, 0.4)  # stores (music, sfx, ambience) before mute

# ── Load images ───────────────────────────────────────────────────────────────
def load_bg(filename):
    if os.path.exists(filename):
        raw = pygame.image.load(filename).convert()
        return pygame.transform.scale(raw, (SCREEN_W, SCREEN_H))
    else:
        surf = pygame.Surface((SCREEN_W, SCREEN_H))
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            pygame.draw.line(surf,(int(180*(1-t*0.3)),int(210*(1-t*0.2)),int(255*(1-t*0.1))),(0,y),(SCREEN_W,y))
        msg = pygame.font.SysFont("Arial",20).render(f"'{filename}' not found",True,(60,30,0))
        surf.blit(msg,(20,20))
        return surf

bg_landing   = load_bg("landing.png")
bg_map       = load_bg("modemap.png")
bg_classroom = load_bg("screenview_png.png")

# ── Load teacher sprites ──────────────────────────────────────────────────────
def load_sprite(filename, height):
    if os.path.exists(filename):
        raw = pygame.image.load(filename).convert_alpha()
        rw, rh = raw.get_size()
        scale = height / rh
        return pygame.transform.smoothscale(raw, (int(rw * scale), height))
    else:
        s = pygame.Surface((int(height * 0.55), height), pygame.SRCALPHA)
        s.fill((180, 120, 60, 200))
        return s

TEACHER_H = 180
teacher_walk_img   = load_sprite("teacher_walk.png",   TEACHER_H)
teacher_caught_img = load_sprite("teacher_caught.png", TEACHER_H)
CHECK_ICON_SIZE = 165
if os.path.exists("check.png"):
    _raw_check = pygame.image.load("check.png").convert_alpha()
    check_img  = pygame.transform.smoothscale(_raw_check, (CHECK_ICON_SIZE, CHECK_ICON_SIZE))
else:
    check_img = None

# ── Load task frame image ─────────────────────────────────────────────────────
def load_frame(filename, width):
    if os.path.exists(filename):
        raw = pygame.image.load(filename).convert_alpha()
        rw, rh = raw.get_size()
        scale  = width / rw
        return pygame.transform.smoothscale(raw, (width, int(rh * scale)))
    else:
        s = pygame.Surface((width, int(width * 0.67)), pygame.SRCALPHA)
        pygame.draw.rect(s, (220, 195, 145, 230), (0, 0, width, int(width * 0.67)), border_radius=16)
        pygame.draw.rect(s, (160, 120,  60, 255), (0, 0, width, int(width * 0.67)), 4, border_radius=16)
        return s

TASK_FRAME_W   = 520
task_frame_img = load_frame("taskframe.png", TASK_FRAME_W)

# ── Load How to Play image ────────────────────────────────────────────────────
HOWTO_IMG_FILE = "how_to_play.png"
if os.path.exists(HOWTO_IMG_FILE):
    _raw_howto = pygame.image.load(HOWTO_IMG_FILE).convert_alpha()
    _hrw, _hrh = _raw_howto.get_size()
    _hscale = min((SCREEN_W - 60) / _hrw, (SCREEN_H - 40) / _hrh, 1.0)
    HPW = int(_hrw * _hscale)
    HPH = int(_hrh * _hscale)
    howto_img = pygame.transform.smoothscale(_raw_howto, (HPW, HPH))
    howto_img_loaded = True
else:
    HPW, HPH = 620, 400
    howto_img = None
    howto_img_loaded = False

HPX = (SCREEN_W - HPW) // 2
HPY = (SCREEN_H - HPH) // 2

# ── Load locked popup image ───────────────────────────────────────────────────
LOCKED_IMG_FILE = "locked.png"
if os.path.exists(LOCKED_IMG_FILE):
    _raw_locked = pygame.image.load(LOCKED_IMG_FILE).convert_alpha()
    _lrw, _lrh  = _raw_locked.get_size()
    _lscale = min((SCREEN_W - 60) / _lrw, (SCREEN_H - 40) / _lrh, 1.0)
    LPW = int(_lrw * _lscale)
    LPH = int(_lrh * _lscale)
    locked_img = pygame.transform.smoothscale(_raw_locked, (LPW, LPH))
    locked_img_loaded = True
else:
    LPW, LPH = 480, 300
    locked_img = None
    locked_img_loaded = False

LPX = (SCREEN_W - LPW) // 2
LPY = (SCREEN_H - LPH) // 2

# Locked popup state
show_locked      = False
locked_anim      = 0.0
LOCKED_SPEED     = 0.12
locked_okay_rect = pygame.Rect(0, 0, 0, 0)

def draw_locked_popup(surf, anim_t):
    global locked_okay_rect
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, int(170 * min(anim_t * 2, 1))))
    surf.blit(overlay, (0, 0))
    scale = 0.6 + 0.4 * anim_t
    pw = int(LPW * scale)
    ph = int(LPH * scale)
    px = SCREEN_W // 2 - pw // 2
    py = SCREEN_H // 2 - ph // 2
    popup_surf = pygame.Surface((LPW, LPH), pygame.SRCALPHA)
    if locked_img_loaded:
        popup_surf.blit(locked_img, (0, 0))
    else:
        pygame.draw.rect(popup_surf, (40, 30, 55, 240), (0, 0, LPW, LPH), border_radius=22)
        pygame.draw.rect(popup_surf, (180, 140, 60, 255), (0, 0, LPW, LPH), 4, border_radius=22)
        lck_cx, lck_cy = LPW // 2, int(LPH * 0.28)
        pygame.draw.rect(popup_surf, (200, 160, 50), (lck_cx - 28, lck_cy, 56, 44), border_radius=8)
        pygame.draw.arc(popup_surf, (200, 160, 50),
                        (lck_cx - 22, lck_cy - 34, 44, 44), 0, math.pi, 6)
        keyhole = pygame.Surface((20, 26), pygame.SRCALPHA)
        pygame.gfxdraw.filled_circle(keyhole, 10, 8, 8, (40, 30, 55, 255))
        pygame.draw.rect(keyhole, (40, 30, 55, 255), (6, 10, 8, 16))
        popup_surf.blit(keyhole, (lck_cx - 10, lck_cy + 9))
        title_s = font_ft_title.render("Lock  Area Locked!", True, (255, 215, 60))
        popup_surf.blit(title_s, (LPW // 2 - title_s.get_width() // 2, int(LPH * 0.52)))
        sub_s = font_ft_body.render("Complete the Classroom first to unlock!", True, (220, 200, 160))
        popup_surf.blit(sub_s, (LPW // 2 - sub_s.get_width() // 2, int(LPH * 0.66)))
    okay_w = int(LPW * 0.23)
    okay_h = int(LPH * 0.10)
    okay_x = LPW // 2 - okay_w // 2
    okay_y = int(LPH * 0.74)
    mx_now, my_now = pygame.mouse.get_pos()
    local_mx = int((mx_now - px) / scale)
    local_my = int((my_now - py) / scale)
    okay_local_rect = pygame.Rect(okay_x, okay_y, okay_w, okay_h)
    okay_hov = okay_local_rect.collidepoint(local_mx, local_my)
    btn_col  = (100, 190, 80) if okay_hov else (70, 155, 55)
    btn_dark = (40, 100, 30)
    pygame.draw.rect(popup_surf, btn_dark, (okay_x + 2, okay_y + 4, okay_w, okay_h), border_radius=okay_h // 2)
    pygame.draw.rect(popup_surf, btn_col,  (okay_x, okay_y, okay_w, okay_h),          border_radius=okay_h // 2)
    okay_lbl    = font_play.render("Okay!", True, WHITE)
    okay_lbl_sh = font_play.render("Okay!", True, (0, 0, 0))
    okay_lbl_sh.set_alpha(60)
    lx = okay_x + okay_w // 2 - okay_lbl.get_width() // 2
    ly = okay_y + okay_h // 2 - okay_lbl.get_height() // 2
    popup_surf.blit(okay_lbl_sh, (lx + 1, ly + 1))
    popup_surf.blit(okay_lbl,    (lx, ly))
    scaled = pygame.transform.smoothscale(popup_surf, (pw, ph))
    surf.blit(scaled, (px, py))
    locked_okay_rect = pygame.Rect(
        px + int(okay_x * scale),
        py + int(okay_y * scale),
        int(okay_w * scale),
        int(okay_h * scale),
    )

# ── Load feed-task sprites ────────────────────────────────────────────────────
def load_png_scaled(filename, target_h):
    if os.path.exists(filename):
        raw = pygame.image.load(filename).convert_alpha()
        rw, rh = raw.get_size()
        tw = int(rw * target_h / rh)
        return pygame.transform.smoothscale(raw, (tw, target_h))
    s = pygame.Surface((int(target_h * 0.8), target_h), pygame.SRCALPHA)
    s.fill((180, 100, 30, 200))
    return s

ft_img_bowl = load_png_scaled("bowl.png",    130)
ft_img_bag  = load_png_scaled("petfood.png", 150)
ft_img_dog  = load_png_scaled("puppy.png",   110)

# ── Fonts ─────────────────────────────────────────────────────────────────────
def load_font(size, bold=False):
    for name in ["Segoe UI","Calibri","Arial"]:
        try: return pygame.font.SysFont(name, size, bold=bold)
        except: continue
    return pygame.font.Font(None, size)

font_large    = load_font(22, bold=True)
font_small    = load_font(13, bold=True)
font_title    = load_font(32, bold=True)
font_map      = load_font(14, bold=True)
font_popup    = load_font(20, bold=True)
font_popup_s  = load_font(15, bold=False)
font_popup_b  = load_font(28, bold=True)
font_task     = load_font(15, bold=True)
font_warn     = load_font(13, bold=True)
font_play     = load_font(24, bold=True)
font_timer    = load_font(36, bold=True)
font_task_g   = load_font(14, bold=True)
font_ft_title = load_font(26, bold=True)
font_ft_body  = load_font(15, bold=False)
font_ft_hint  = load_font(13, bold=False)
font_ft_big   = load_font(30, bold=True)

# ── Smooth rounded rect ───────────────────────────────────────────────────────
def draw_smooth_rect(surf, color, rect, radius=12):
    x, y, w, h = rect
    pygame.draw.rect(surf, color, (x + radius, y, w - 2*radius, h))
    pygame.draw.rect(surf, color, (x, y + radius, w, h - 2*radius))
    for cx, cy in [(x+radius, y+radius), (x+w-radius-1, y+radius),
                   (x+radius, y+h-radius-1), (x+w-radius-1, y+h-radius-1)]:
        pygame.gfxdraw.aacircle(surf, cx, cy, radius, color)
        pygame.gfxdraw.filled_circle(surf, cx, cy, radius, color)

def draw_rounded_rect(surf, colour, rect, r=12, border=0, border_colour=None):
    pygame.draw.rect(surf, colour, rect, border_radius=r)
    if border and border_colour:
        pygame.draw.rect(surf, border_colour, rect, border, border_radius=r)

# ── Landing button ────────────────────────────────────────────────────────────
def draw_modern_button(surf, rect, col_main, col_dark, col_hover, label, icon, hovered):
    x, y, w, h = rect
    col = col_hover if hovered else col_main
    for i in range(8, 0, -1):
        shadow_surf = pygame.Surface((w + i*2, h + i*2), pygame.SRCALPHA)
        draw_smooth_rect(shadow_surf, (0, 0, 0), (0, 0, w+i*2, h+i*2), radius=h//2)
        shadow_surf.set_alpha(int(120 * (i / 8) ** 2) // 4)
        surf.blit(shadow_surf, (x - i, y - i + 6))
    draw_smooth_rect(surf, col_dark, (x, y+5, w, h), radius=h//2)
    draw_smooth_rect(surf, col, (x, y, w, h), radius=h//2)
    icon_s   = font_large.render(icon,  True, WHITE)
    label_s  = font_large.render(label, True, WHITE)
    shadow_s = font_large.render(label, True, (0,0,0))
    shadow_s.set_alpha(60)
    total_w = icon_s.get_width() + 12 + label_s.get_width()
    sx = x + (w - total_w) // 2
    cy = y + (h - label_s.get_height()) // 2
    surf.blit(shadow_s, (sx + icon_s.get_width() + 12 + 1, cy + 1))
    surf.blit(icon_s,   (sx, y + (h - icon_s.get_height()) // 2))
    surf.blit(label_s,  (sx + icon_s.get_width() + 12, cy))

# ── Classroom popup image ─────────────────────────────────────────────────────
POPUP_IMG_FILE = "Class_info_png.png"
if os.path.exists(POPUP_IMG_FILE):
    _raw_popup = pygame.image.load(POPUP_IMG_FILE).convert_alpha()
    _rw, _rh   = _raw_popup.get_size()
    max_w = SCREEN_W - 60
    max_h = SCREEN_H - 40
    scale_fit = min(max_w / _rw, max_h / _rh, 1.0)
    PW = int(_rw * scale_fit)
    PH = int(_rh * scale_fit)
    popup_img = pygame.transform.smoothscale(_raw_popup, (PW, PH))
    popup_img_loaded = True
else:
    PW, PH = 660, 420
    popup_img = None
    popup_img_loaded = False

PX = (SCREEN_W - PW) // 2
PY = (SCREEN_H - PH) // 2

PLAY_W     = int(PW * 0.25)
PLAY_H     = int(PH * 0.08)
CLOSE_SIZE = int(min(PW, PH) * 0.07)

popup_play_hovered  = False
popup_close_hovered = False

def _play_rect_local():
    cx = PW // 2
    cy = int(PH * 0.850)
    return pygame.Rect(cx - PLAY_W // 2, cy - PLAY_H // 2, PLAY_W, PLAY_H)

def _close_rect_local():
    cx = int(PW * 0.873)
    cy = int(PH * 0.090)
    return pygame.Rect(cx - CLOSE_SIZE // 2, cy - CLOSE_SIZE // 2, CLOSE_SIZE, CLOSE_SIZE)

def draw_popup(surf, play_hov, close_hov, anim_t):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, int(170 * min(anim_t * 2, 1))))
    surf.blit(overlay, (0, 0))
    scale = 0.6 + 0.4 * anim_t
    pw = int(PW * scale)
    ph = int(PH * scale)
    px = SCREEN_W // 2 - pw // 2
    py = SCREEN_H // 2 - ph // 2
    popup_surf = pygame.Surface((PW, PH), pygame.SRCALPHA)
    if popup_img_loaded:
        popup_surf.blit(popup_img, (0, 0))
    else:
        pygame.draw.rect(popup_surf, (245, 230, 195), (0, 0, PW, PH), border_radius=20)
        pygame.draw.rect(popup_surf, (139, 90, 43),   (0, 0, PW, PH), 4, border_radius=20)
        msg = font_popup_b.render("Class_info_png.png not found", True, (120, 60, 20))
        popup_surf.blit(msg, (PW//2 - msg.get_width()//2, PH//2 - msg.get_height()//2))
    pr = _play_rect_local()
    if play_hov:
        glow = pygame.Surface((pr.w + 12, pr.h + 12), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 255, 255, 60), (0, 0, pr.w+12, pr.h+12), border_radius=(pr.h+12)//2)
        popup_surf.blit(glow, (pr.x - 6, pr.y - 6))
        pygame.draw.rect(popup_surf, (200, 255, 180), (pr.x, pr.y, pr.w, pr.h), 3, border_radius=pr.h//2)
    cr = _close_rect_local()
    if close_hov:
        glow = pygame.Surface((cr.w + 10, cr.h + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 120, 100, 80), (0, 0, cr.w+10, cr.h+10))
        popup_surf.blit(glow, (cr.x - 5, cr.y - 5))
        pygame.draw.ellipse(popup_surf, (255, 200, 190), (cr.x, cr.y, cr.w, cr.h), 3)
    scaled = pygame.transform.smoothscale(popup_surf, (pw, ph))
    surf.blit(scaled, (px, py))

# ── How to Play popup ─────────────────────────────────────────────────────────
howto_close_rect = pygame.Rect(0, 0, 0, 0)

def draw_howto_popup(surf, anim_t):
    global howto_close_rect
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, int(170 * min(anim_t * 2, 1))))
    surf.blit(overlay, (0, 0))
    scale = 0.6 + 0.4 * anim_t
    pw = int(HPW * scale)
    ph = int(HPH * scale)
    px = SCREEN_W // 2 - pw // 2
    py = SCREEN_H // 2 - ph // 2
    popup_surf = pygame.Surface((HPW, HPH), pygame.SRCALPHA)
    if howto_img_loaded:
        popup_surf.blit(howto_img, (0, 0))
    else:
        pygame.draw.rect(popup_surf, (245, 230, 195), (0, 0, HPW, HPH), border_radius=20)
        pygame.draw.rect(popup_surf, (139, 90, 43),   (0, 0, HPW, HPH), 4, border_radius=20)
        msg = font_popup_b.render("how_to_play.png not found", True, (120, 60, 20))
        popup_surf.blit(msg, (HPW//2 - msg.get_width()//2, HPH//2 - msg.get_height()//2))
    scaled = pygame.transform.smoothscale(popup_surf, (pw, ph))
    surf.blit(scaled, (px, py))
    cs = 32
    howto_close_rect = pygame.Rect(px + pw - cs - 8, py + 8, cs, cs)
    close_hov = howto_close_rect.collidepoint(*pygame.mouse.get_pos())
    col = (210, 70, 50) if close_hov else (170, 50, 30)
    pygame.draw.circle(surf, col, howto_close_rect.center, howto_close_rect.w // 2)
    pygame.draw.circle(surf, (255, 255, 255), howto_close_rect.center, howto_close_rect.w // 2, 2)
    x_s = font_ft_body.render("X", True, WHITE)
    surf.blit(x_s, (howto_close_rect.centerx - x_s.get_width() // 2,
                    howto_close_rect.centery - x_s.get_height() // 2))

# ── Settings popup ────────────────────────────────────────────────────────────
show_settings            = False
settings_anim            = 0.0
SETTINGS_SPEED           = 0.12
settings_close_rect      = pygame.Rect(0, 0, 0, 0)
settings_dragging_slider = None   # "music" | "sfx" | "ambience" | None

SPW_BASE = 480
SPH_BASE = 340

def draw_settings_popup(surf, anim_t):
    global settings_close_rect, vol_music, vol_sfx, vol_ambience

    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, int(170 * min(anim_t * 2, 1))))
    surf.blit(overlay, (0, 0))

    scale  = 0.6 + 0.4 * anim_t
    spw_s  = int(SPW_BASE * scale)
    sph_s  = int(SPH_BASE * scale)
    spx    = SCREEN_W // 2 - spw_s // 2
    spy    = SCREEN_H // 2 - sph_s // 2

    panel = pygame.Surface((SPW_BASE, SPH_BASE), pygame.SRCALPHA)

    # Background
    pygame.draw.rect(panel, (30, 25, 50, 245), (0, 0, SPW_BASE, SPH_BASE), border_radius=22)
    pygame.draw.rect(panel, (120, 90, 180, 255), (0, 0, SPW_BASE, SPH_BASE), 3, border_radius=22)

    # Banner
    banner_h = 54
    pygame.draw.rect(panel, (45, 30, 80, 240), (0, 0, SPW_BASE, banner_h), border_radius=22)
    pygame.draw.rect(panel, (45, 30, 80, 240), (0, banner_h // 2, SPW_BASE, banner_h // 2))
    title_s = font_ft_title.render("Settings", True, (220, 195, 255))
    panel.blit(title_s, (SPW_BASE // 2 - title_s.get_width() // 2,
                          banner_h // 2 - title_s.get_height() // 2))

    sliders = [
        ("Music Volume",    vol_music,    "music"),
        ("SFX Volume",      vol_sfx,      "sfx"),
        ("Ambience Volume", vol_ambience, "ambience"),
    ]
    bar_x   = 60
    bar_w   = SPW_BASE - 160
    bar_h   = 18
    start_y = 90
    row_gap = 72

    for si, (label, val, key) in enumerate(sliders):
        by = start_y + si * row_gap

        lbl_s = font_ft_body.render(label, True, (200, 175, 235))
        panel.blit(lbl_s, (bar_x, by - 20))

        # Track background
        pygame.draw.rect(panel, (20, 15, 35), (bar_x, by, bar_w, bar_h), border_radius=9)

        # Fill
        fill_w = int(bar_w * val)
        if fill_w > 0:
            pygame.draw.rect(panel, (130, 90, 210), (bar_x, by, fill_w, bar_h), border_radius=9)

        # Track border
        pygame.draw.rect(panel, (100, 75, 160, 160), (bar_x, by, bar_w, bar_h), 2, border_radius=9)

        # Knob
        knob_x = bar_x + fill_w
        knob_y = by + bar_h // 2
        pygame.gfxdraw.filled_circle(panel, knob_x, knob_y, 11, (210, 185, 255, 230))
        pygame.gfxdraw.aacircle(panel,     knob_x, knob_y, 11, (160, 130, 220, 255))

        # Percentage label
        pct_s = font_ft_hint.render(f"{int(val * 100)}%", True, (180, 155, 220))
        panel.blit(pct_s, (bar_x + bar_w + 10,
                            by + bar_h // 2 - pct_s.get_height() // 2))

    scaled_panel = pygame.transform.smoothscale(panel, (spw_s, sph_s))
    surf.blit(scaled_panel, (spx, spy))

    # Close button
    cs = 32
    settings_close_rect = pygame.Rect(spx + spw_s - cs - 8, spy + 8, cs, cs)
    close_hov = settings_close_rect.collidepoint(*pygame.mouse.get_pos())
    col = (210, 70, 50) if close_hov else (170, 50, 30)
    pygame.draw.circle(surf, col, settings_close_rect.center, settings_close_rect.w // 2)
    pygame.draw.circle(surf, (255, 255, 255), settings_close_rect.center, settings_close_rect.w // 2, 2)
    x_s = font_ft_body.render("X", True, WHITE)
    surf.blit(x_s, (settings_close_rect.centerx - x_s.get_width() // 2,
                    settings_close_rect.centery - x_s.get_height() // 2))

# ── Landing buttons ───────────────────────────────────────────────────────────
LW = 265; LH = 52
LX = SCREEN_W - LW - 55
LY = int(SCREEN_H * 0.615)
LG = int(SCREEN_H * 0.118)

landing_buttons = [
    {"id":"start",    "label":"Start Game",  "icon":">", "rect":(LX, LY,          LW, LH), "col":BTN_GREEN,  "dark":BTN_GREEN_D,  "hover":BTN_GREEN_H},
    {"id":"settings", "label":"Settings",    "icon":"#", "rect":(LX, LY + LG,     LW, LH), "col":BTN_BLUE,   "dark":BTN_BLUE_D,   "hover":BTN_BLUE_H},
    {"id":"howto",    "label":"How to Play", "icon":"?", "rect":(LX, LY + LG * 2, LW, LH), "col":BTN_YELLOW, "dark":BTN_YELLOW_D, "hover":BTN_YELLOW_H},
]

# ── Map button colors ─────────────────────────────────────────────────────────
MAP_BLUE       = (55,  115, 195); MAP_BLUE_H   = (75,  140, 225); MAP_BLUE_D   = (30,  75,  140)
MAP_RED        = (155, 35,  35);  MAP_RED_H    = (185, 50,  50);  MAP_RED_D    = (100, 18,  18)
MAP_NAVY       = (35,  60,  110); MAP_NAVY_H   = (50,  85,  145); MAP_NAVY_D   = (18,  35,  70)

# ── Mode select button rects ──────────────────────────────────────────────────
MAP_BTN_W   = 220
MAP_BTN_H   = 48
MAP_BTN_GAP = 100
MAP_BTN_CX  = SCREEN_W // 2
MAP_BTN_Y   = SCREEN_H // 2 + 105

CARD_CLASSROOM_RECT = pygame.Rect(MAP_BTN_CX - MAP_BTN_W - MAP_BTN_GAP // 2, MAP_BTN_Y, MAP_BTN_W, MAP_BTN_H)
CARD_LIBRARY_RECT   = pygame.Rect(MAP_BTN_CX + MAP_BTN_GAP // 2,              MAP_BTN_Y, MAP_BTN_W, MAP_BTN_H)

BACK_EXIT_W    = 218
BACK_EXIT_H    = 50
BACK_EXIT_RECT = pygame.Rect(SCREEN_W // 2 - BACK_EXIT_W // 2, SCREEN_H - 65, BACK_EXIT_W, BACK_EXIT_H)

def draw_map_button(surf, rect, col_main, col_dark, col_hover, label, icon, hovered):
    x, y, w, h = rect
    r = 10
    col = col_hover if hovered else col_main
    shadow = pygame.Surface((w + 4, h + 6), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 80), (0, 0, w + 4, h + 6), border_radius=r + 2)
    surf.blit(shadow, (x - 2, y + 4))
    pygame.draw.rect(surf, col_dark, (x, y + 4, w, h), border_radius=r)
    pygame.draw.rect(surf, col, (x, y, w, h), border_radius=r)
    sheen = pygame.Surface((w - 4, h // 2), pygame.SRCALPHA)
    for hy in range(h // 2):
        a = int(70 * (1 - hy / (h // 2)))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, hy), (w - 4, hy))
    surf.blit(sheen, (x + 2, y + 2))
    pygame.draw.rect(surf, (255, 255, 255, 60) if hovered else (0, 0, 0, 40),
                     (x, y, w, h), 2, border_radius=r)
    icon_s  = font_large.render(icon,  True, WHITE)
    label_s = font_large.render(label, True, WHITE)
    lbl_sh  = font_large.render(label, True, (0, 0, 0))
    lbl_sh.set_alpha(60)
    total_w = icon_s.get_width() + 10 + label_s.get_width()
    sx = x + (w - total_w) // 2
    cy = y + (h - label_s.get_height()) // 2
    surf.blit(lbl_sh,  (sx + icon_s.get_width() + 11, cy + 1))
    surf.blit(icon_s,  (sx, y + (h - icon_s.get_height()) // 2))
    surf.blit(label_s, (sx + icon_s.get_width() + 10, cy))

def draw_mode_select(surf, hov):
    surf.blit(bg_map, (0, 0))
    draw_map_button(surf, tuple(CARD_CLASSROOM_RECT),
                    MAP_BLUE, MAP_BLUE_D, MAP_BLUE_H,
                    "PLAY", "", hov == "classroom")
    draw_map_button(surf, tuple(CARD_LIBRARY_RECT),
                    MAP_RED, MAP_RED_D, MAP_RED_H,
                    "PLAY", "", hov == "library")
    draw_map_button(surf, tuple(BACK_EXIT_RECT),
                    MAP_NAVY, MAP_NAVY_D, MAP_NAVY_H,
                    "BACK / EXIT", "", hov == "back")
    draw_mute_button(surf)

# ── Classroom game constants ──────────────────────────────────────────────────
CLASSROOM_TIME = 120
CLASSROOM_TASKS = [
    "Feed your pet",
    "Fill the water bowl",
    "Calm your pet",
    "Distract with toys",
    "Clean up any mess",
]
TASK_ICON_COLS = [
    (210, 80,  60),
    (60,  140, 210),
    (210, 155, 80),
    (100, 175, 60),
    (160, 130, 100),
]

# ── Teacher constants ─────────────────────────────────────────────────────────
TEACHER_INTERVAL_MIN  = 5.0
TEACHER_INTERVAL_MAX  = 11.0
TEACHER_WALK_SPEED    = 130
TEACHER_PAUSE_TIME    = 2.5
TEACHER_WARN_TIME     = 2.5
TEACHER_PATROL_MIN    = 2.0
TEACHER_PATROL_MAX    = 3.5

teacher_state         = "idle"
teacher_x             = float(-300)
teacher_direction     = 1
teacher_next_time     = 8.0
teacher_pause_timer   = 0.0
teacher_warn_timer    = 0.0
teacher_caught_player = False
teacher_suspicion     = False
teacher_patrol_timer  = 0.0

classroom_timer   = CLASSROOM_TIME
classroom_running = False
tasks_done        = [False] * len(CLASSROOM_TASKS)
task_anim         = [0.0]  * len(CLASSROOM_TASKS)

# ── Helper: draw warning overlay on top of everything ────────────────────────
def draw_warning_overlay_on_top(surf):
    if teacher_state not in ("walking", "patrolling"):
        return
    pulse      = abs(math.sin(pygame.time.get_ticks() * 0.006))
    warn_alpha = int(180 + 75 * pulse)
    banner = pygame.Surface((SCREEN_W, 30), pygame.SRCALPHA)
    banner.fill((200, 30, 20, int(warn_alpha * 0.55)))
    surf.blit(banner, (0, SCREEN_H - 30))
    warn_msg = font_small.render(
        "WARNING  TEACHER NEARBY — close your task and stay still!",
        True, (255, 230, 80)
    )
    surf.blit(warn_msg, (SCREEN_W // 2 - warn_msg.get_width() // 2, SCREEN_H - 22))
    vignette = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    edge_alpha = int(80 * pulse)
    pygame.draw.rect(vignette, (220, 30, 20, edge_alpha),
                     (0, 0, SCREEN_W, SCREEN_H), 22)
    surf.blit(vignette, (0, 0))

# ══════════════════════════════════════════════════════════════════════════════
# ── Feed Task ─────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
ft_active      = False
ft_progress    = 0.0
ft_dragging    = False
ft_drag_offset = (0, 0)
ft_bag_pos     = [0, 0]
ft_bag_home    = [0, 0]
ft_wobble_t    = 0.0
ft_returning   = False
ft_kibbles     = []
ft_flash_t     = 0.0
ft_miss_t      = 0.0
ft_shake_t     = 0.0
ft_anim_t      = 0.0
ft_close_rect  = pygame.Rect(0, 0, 0, 0)
ft_bowl_centre = (0, 0)
FT_PANEL_W = 560
FT_PANEL_H = 420

def ft_open():
    global ft_active, ft_progress, ft_dragging, ft_returning
    global ft_kibbles, ft_flash_t, ft_miss_t, ft_shake_t
    global ft_wobble_t, ft_anim_t, ft_bag_pos, ft_bag_home, ft_bowl_centre
    ft_active      = True
    ft_progress    = 0.0
    ft_dragging    = False
    ft_returning   = False
    ft_kibbles     = []
    ft_flash_t     = 0.0
    ft_miss_t      = 0.0
    ft_shake_t     = 0.0
    ft_wobble_t    = 0.0
    ft_anim_t      = 0.0
    ft_bag_home    = [-999, -999]
    ft_bag_pos     = [-999, -999]
    ft_bowl_centre = (-999, -999)

class _Kibble:
    def __init__(self, x, y):
        angle  = random.uniform(-math.pi * 0.9, -math.pi * 0.1)
        speed  = random.uniform(90, 200)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * speed * random.uniform(0.6, 1.0)
        self.vy = math.sin(angle) * speed
        self.r  = random.randint(4, 8)
        self.life = 1.0
        self.decay = random.uniform(1.4, 2.2)
        shade = random.randint(80, 130)
        self.col = (shade, int(shade * 0.55), 15)

    def update(self, dt):
        self.vy  += 420 * dt
        self.x   += self.vx * dt
        self.y   += self.vy * dt
        self.life -= self.decay * dt
        return self.life > 0

    def draw(self, surf):
        alpha = int(max(0, self.life) * 255)
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.gfxdraw.filled_circle(s, self.r, self.r, self.r, (*self.col, alpha))
        surf.blit(s, (int(self.x) - self.r, int(self.y) - self.r))

def ft_try_drop(mx, my):
    global ft_progress, ft_flash_t, ft_miss_t, ft_shake_t
    global ft_kibbles, ft_bag_pos, ft_returning, ft_bowl_centre
    bscx, bscy = ft_bowl_centre
    dist = math.hypot(mx - bscx, my - bscy)
    if dist <= FT_SNAP_RADIUS:
        ft_progress = min(1.0, ft_progress + FT_DROP_PER_DRAG)
        ft_flash_t  = 0.35
        for _ in range(random.randint(8, 14)):
            ft_kibbles.append(_Kibble(bscx, bscy - 20))
        ft_bag_pos   = list(ft_bag_home)
        ft_returning = False
        play_sound(sfx_click)
    else:
        ft_miss_t    = 0.30
        ft_shake_t   = 0.35
        ft_returning = True

def ft_update(events, dt):
    global ft_active, ft_anim_t, ft_flash_t, ft_miss_t, ft_shake_t
    global ft_wobble_t, ft_kibbles, ft_dragging, ft_drag_offset
    global ft_bag_pos, ft_returning, ft_close_rect, ft_bowl_centre
    if not ft_active:
        return False, False
    if ft_anim_t < 1.0:
        ft_anim_t = min(1.0, ft_anim_t + dt * 4.5)
    ft_flash_t  = max(0.0, ft_flash_t - dt)
    ft_miss_t   = max(0.0, ft_miss_t  - dt)
    ft_shake_t  = max(0.0, ft_shake_t - dt)
    ft_wobble_t += dt
    ft_kibbles[:] = [k for k in ft_kibbles if k.update(dt)]
    if ft_returning and not ft_dragging:
        hx, hy = ft_bag_home
        bx, by = ft_bag_pos
        dx, dy = hx - bx, hy - by
        dist   = math.hypot(dx, dy)
        move   = FT_DRIFT_SPEED * 1.8 * dt
        if dist <= move + 1:
            ft_bag_pos[:] = ft_bag_home
            ft_returning  = False
        else:
            factor = move / dist
            ft_bag_pos[0] += dx * factor
            ft_bag_pos[1] += dy * factor
    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            ft_active = False
            return False, True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if ft_close_rect.collidepoint(mx, my):
                play_sound(sfx_click)
                ft_active = False
                return False, True
            bw = ft_img_bag.get_width()
            bh = ft_img_bag.get_height()
            bx = ft_bag_pos[0] - bw // 2
            by = ft_bag_pos[1] - bh // 2
            bag_rect = pygame.Rect(bx, by, bw, bh)
            if bag_rect.collidepoint(mx, my):
                play_sound(sfx_click)
                ft_dragging    = True
                ft_returning   = False
                ft_drag_offset = (mx - ft_bag_pos[0], my - ft_bag_pos[1])
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if ft_dragging:
                ft_dragging = False
                ft_try_drop(mx, my)
    if ft_dragging:
        ft_bag_pos[0] = mx - ft_drag_offset[0]
        ft_bag_pos[1] = my - ft_drag_offset[1]
    if ft_progress >= 1.0:
        play_sound(sfx_task_complete)
        ft_active = False
        return True, False
    return False, False

def ft_draw(surf):
    global ft_close_rect, ft_bowl_centre, ft_bag_home, ft_bag_pos
    if not ft_active:
        return
    PW    = FT_PANEL_W
    PH    = FT_PANEL_H
    scale = 0.55 + 0.45 * (1 - (1 - ft_anim_t) ** 3)
    shake_x = 0
    shake_y = 0
    if ft_shake_t > 0:
        intensity = ft_shake_t / 0.35
        shake_x = int(random.uniform(-7, 7) * intensity)
        shake_y = int(random.uniform(-4, 4) * intensity)
    px = (SCREEN_W - int(PW * scale)) // 2 + shake_x
    py = (SCREEN_H - int(PH * scale)) // 2 + shake_y
    bowl_local_cx  = PW // 2
    bowl_local_cy  = int(PH * 0.72)
    new_bowl_cx    = px + int(bowl_local_cx * scale)
    new_bowl_cy    = py + int(bowl_local_cy * scale)
    dog_local_x    = 32
    dog_local_cy   = bowl_local_cy
    dog_screen_x   = px + int(dog_local_x * scale)
    dog_screen_cy  = py + int(dog_local_cy * scale)
    new_bag_home_x = px + int(PW * 0.78 * scale)
    new_bag_home_y = py + int(PH * 0.46 * scale)
    if ft_bag_pos[0] == -999:
        ft_bag_pos[0] = new_bag_home_x
        ft_bag_pos[1] = new_bag_home_y
    if ft_bag_home[0] != -999 and not ft_dragging:
        ft_bag_pos[0] += new_bag_home_x - ft_bag_home[0]
        ft_bag_pos[1] += new_bag_home_y - ft_bag_home[1]
    ft_bag_home    = [new_bag_home_x, new_bag_home_y]
    ft_bowl_centre = (new_bowl_cx, new_bowl_cy)
    dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, int(165 * ft_anim_t)))
    surf.blit(dim, (0, 0))
    panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*PARCHMENT, 245), (0, 0, PW, PH), border_radius=20)
    pygame.draw.rect(panel, (*WOOD_BROWN, 255), (0, 0, PW, PH), 3, border_radius=20)
    banner_h = 54
    pygame.draw.rect(panel, (*WOOD_BROWN, 230), (0, 0, PW, banner_h), border_radius=20)
    pygame.draw.rect(panel, (*WOOD_BROWN, 230), (0, banner_h // 2, PW, banner_h // 2))
    title_s = font_ft_title.render("Feed Your Pet!", True, WHITE)
    panel.blit(title_s, (PW // 2 - title_s.get_width() // 2, banner_h // 2 - title_s.get_height() // 2))
    bar_x, bar_y = 60, 72
    bar_w, bar_h = PW - 120, 22
    pygame.draw.rect(panel, FT_BAR_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=11)
    fill_w = int(bar_w * min(ft_progress, 1.0))
    if fill_w > 0:
        for xi in range(fill_w):
            t = xi / max(bar_w, 1)
            r = int(FT_BAR_FILL_A[0] + (FT_BAR_FILL_B[0] - FT_BAR_FILL_A[0]) * t)
            g = int(FT_BAR_FILL_A[1] + (FT_BAR_FILL_B[1] - FT_BAR_FILL_A[1]) * t)
            b = int(FT_BAR_FILL_A[2] + (FT_BAR_FILL_B[2] - FT_BAR_FILL_A[2]) * t)
            pygame.draw.line(panel, (r, g, b),
                             (bar_x + xi, bar_y + 1), (bar_x + xi, bar_y + bar_h - 2))
    sheen = pygame.Surface((bar_w, bar_h // 2), pygame.SRCALPHA)
    for yi in range(bar_h // 2):
        a = int(50 * (1 - yi / (bar_h // 2)))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, yi), (bar_w, yi))
    panel.blit(sheen, (bar_x, bar_y))
    pygame.draw.rect(panel, (100, 60, 15, 180), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=11)
    pct_s = font_ft_hint.render(f"{int(ft_progress * 100)}%", True, WOOD_BROWN)
    panel.blit(pct_s, (bar_x + bar_w + 6, bar_y + bar_h // 2 - pct_s.get_height() // 2))
    hint_s = font_ft_body.render("Drag the food bag and drop it on the bowl!", True, WOOD_BROWN)
    panel.blit(hint_s, (PW // 2 - hint_s.get_width() // 2, 100))
    ring_r = FT_SNAP_RADIUS - 8
    pulse  = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.6 + 0.4
    ring_s = pygame.Surface((ring_r * 2 + 6, ring_r * 2 + 6), pygame.SRCALPHA)
    pygame.gfxdraw.aacircle(ring_s, ring_r + 3, ring_r + 3, ring_r,
                             (100, 220, 80, int(80 * pulse)))
    panel.blit(ring_s, (bowl_local_cx - ring_r - 3, bowl_local_cy - ring_r - 3))
    if ft_flash_t > 0:
        alpha = int(ft_flash_t / 0.35 * 90)
        flash = pygame.Surface((PW, PH), pygame.SRCALPHA)
        flash.fill((80, 230, 60, alpha))
        panel.blit(flash, (0, 0))
    if ft_miss_t > 0:
        alpha  = int(ft_miss_t / 0.30 * 80)
        miss_s = pygame.Surface((PW, PH), pygame.SRCALPHA)
        miss_s.fill((230, 60, 40, alpha))
        panel.blit(miss_s, (0, 0))
    if ft_progress >= 1.0:
        done_s  = font_ft_big.render("Bowl Filled!", True, FT_GREEN)
        done_sh = font_ft_big.render("Bowl Filled!", True, (0, 0, 0))
        done_sh.set_alpha(60)
        cx = PW // 2 - done_s.get_width() // 2
        cy = PH - 50
        panel.blit(done_sh, (cx + 2, cy + 2))
        panel.blit(done_s,  (cx, cy))
    scaled_panel = pygame.transform.smoothscale(panel, (int(PW * scale), int(PH * scale)))
    surf.blit(scaled_panel, (px, py))
    bw_img = ft_img_bowl.get_width()
    bh_img = ft_img_bowl.get_height()
    surf.blit(ft_img_bowl, (new_bowl_cx - bw_img // 2, new_bowl_cy - bh_img // 2))
    dw_img = ft_img_dog.get_width()
    dh_img = ft_img_dog.get_height()
    surf.blit(ft_img_dog, (dog_screen_x, dog_screen_cy - dh_img // 2 - 10))
    cs = 32
    ft_close_rect = pygame.Rect(px + int(PW * scale) - cs - 8, py + 8, cs, cs)
    close_hov = ft_close_rect.collidepoint(*pygame.mouse.get_pos())
    col = (210, 70, 50) if close_hov else (170, 50, 30)
    pygame.draw.circle(surf, col, ft_close_rect.center, ft_close_rect.w // 2)
    pygame.draw.circle(surf, (255, 255, 255), ft_close_rect.center, ft_close_rect.w // 2, 2)
    x_s = font_ft_body.render("X", True, WHITE)
    surf.blit(x_s, (ft_close_rect.centerx - x_s.get_width() // 2,
                    ft_close_rect.centery - x_s.get_height() // 2))
    if ft_dragging:
        wobble_x = math.sin(ft_wobble_t * FT_WOBBLE_FREQ * 2 * math.pi) * FT_DRAG_WOBBLE_STRENGTH
        wobble_y = math.cos(ft_wobble_t * FT_WOBBLE_FREQ * 1.3 * 2 * math.pi) * FT_DRAG_WOBBLE_STRENGTH * 0.5
        angle    = math.sin(ft_wobble_t * FT_WOBBLE_FREQ * 2 * math.pi) * 12
    else:
        wobble_x, wobble_y, angle = 0, 0, 0
    rotated  = pygame.transform.rotate(ft_img_bag, angle)
    rw, rh   = rotated.get_size()
    bx2      = int(ft_bag_pos[0] + wobble_x) - rw // 2
    by2      = int(ft_bag_pos[1] + wobble_y) - rh // 2
    shadow = pygame.Surface((rw + 8, 18), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 60), (0, 0, rw + 8, 18))
    surf.blit(shadow, (bx2 - 4, by2 + rh - 8))
    dist_to_bowl = math.hypot(ft_bag_pos[0] - new_bowl_cx, ft_bag_pos[1] - new_bowl_cy)
    if dist_to_bowl < FT_SNAP_RADIUS + 20:
        glow = pygame.Surface((rw + 20, rh + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow, (80, 230, 60, 40), (0, 0, rw + 20, rh + 20))
        surf.blit(glow, (bx2 - 10, by2 - 10))
    surf.blit(rotated, (bx2, by2))
    for k in ft_kibbles:
        k.draw(surf)
    draw_warning_overlay_on_top(surf)

# ══════════════════════════════════════════════════════════════════════════════
# ── Water Task ────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
WT_PANEL_W        = 540
WT_PANEL_H        = 400
wt_active         = False
wt_progress       = 0.0
wt_anim_t         = 0.0
wt_close_rect     = pygame.Rect(0, 0, 0, 0)
wt_flash_t        = 0.0
wt_ripples        = []
wt_btn_rect       = pygame.Rect(0, 0, 0, 0)
wt_btn_press_t    = 0.0
wt_drain_rate     = 0.045
wt_fill_per_click = 0.038
wt_wave_t         = 0.0

class _Ripple:
    def __init__(self, x, y):
        self.x     = float(x)
        self.y     = float(y)
        self.r     = 4.0
        self.life  = 1.0
        self.decay = 2.2

    def update(self, dt):
        self.r    += 52 * dt
        self.life -= self.decay * dt
        return self.life > 0

    def draw(self, surf):
        alpha = int(max(0, self.life) * 190)
        ir = int(self.r)
        if ir < 2:
            return
        s = pygame.Surface((ir * 2 + 2, ir * 2 + 2), pygame.SRCALPHA)
        pygame.gfxdraw.aacircle(s, ir + 1, ir + 1, ir, (100, 200, 255, alpha))
        surf.blit(s, (int(self.x) - ir - 1, int(self.y) - ir - 1))

def wt_open():
    global wt_active, wt_progress, wt_anim_t, wt_flash_t
    global wt_ripples, wt_btn_press_t, wt_wave_t
    wt_active      = True
    wt_progress    = 0.0
    wt_anim_t      = 0.0
    wt_flash_t     = 0.0
    wt_btn_press_t = 0.0
    wt_wave_t      = 0.0
    wt_ripples     = []

def wt_update(events, dt):
    global wt_active, wt_progress, wt_anim_t, wt_flash_t
    global wt_ripples, wt_btn_press_t, wt_close_rect, wt_btn_rect, wt_wave_t
    if not wt_active:
        return False, False
    if wt_anim_t < 1.0:
        wt_anim_t = min(1.0, wt_anim_t + dt * 4.5)
    wt_flash_t     = max(0.0, wt_flash_t     - dt)
    wt_btn_press_t = max(0.0, wt_btn_press_t - dt)
    wt_wave_t     += dt
    wt_progress = max(0.0, wt_progress - wt_drain_rate * dt)
    wt_ripples[:] = [r for r in wt_ripples if r.update(dt)]
    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            wt_active = False
            return False, True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if wt_close_rect.collidepoint(mx, my):
                play_sound(sfx_click)
                wt_active = False
                return False, True
            if wt_btn_rect.collidepoint(mx, my):
                play_sound(sfx_click)
                wt_progress    = min(1.0, wt_progress + wt_fill_per_click)
                wt_flash_t     = 0.18
                wt_btn_press_t = 0.12
                bowl_cx = SCREEN_W // 2
                bowl_cy = int(SCREEN_H * 0.595)
                spread  = random.randint(-36, 36)
                wt_ripples.append(_Ripple(bowl_cx + spread, bowl_cy))
    if wt_progress >= 1.0:
        wt_progress = 1.0
        play_sound(sfx_task_complete)
        wt_active = False
        return True, False
    return False, False

def wt_draw(surf):
    global wt_close_rect, wt_btn_rect
    if not wt_active:
        return
    PW    = WT_PANEL_W
    PH    = WT_PANEL_H
    scale = 0.55 + 0.45 * (1 - (1 - wt_anim_t) ** 3)
    px = (SCREEN_W - int(PW * scale)) // 2
    py = (SCREEN_H - int(PH * scale)) // 2
    dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, int(165 * wt_anim_t)))
    surf.blit(dim, (0, 0))
    panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*PARCHMENT, 245), (0, 0, PW, PH), border_radius=20)
    pygame.draw.rect(panel, (*WOOD_BROWN, 255), (0, 0, PW, PH), 3, border_radius=20)
    banner_h = 54
    banner_col = (26, 90, 160)
    pygame.draw.rect(panel, (*banner_col, 230), (0, 0, PW, banner_h), border_radius=20)
    pygame.draw.rect(panel, (*banner_col, 230), (0, banner_h // 2, PW, banner_h // 2))
    title_s = font_ft_title.render("Fill the Water Bowl!", True, WHITE)
    panel.blit(title_s, (PW // 2 - title_s.get_width() // 2,
                          banner_h // 2 - title_s.get_height() // 2))
    bar_x, bar_y = 60, 70
    bar_w, bar_h = PW - 120, 22
    pygame.draw.rect(panel, WT_BAR_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=11)
    fill_w = int(bar_w * min(wt_progress, 1.0))
    if fill_w > 0:
        for xi in range(fill_w):
            t = xi / max(bar_w, 1)
            r = int(WT_BAR_FILL_A[0] + (WT_BAR_FILL_B[0] - WT_BAR_FILL_A[0]) * t)
            g = int(WT_BAR_FILL_A[1] + (WT_BAR_FILL_B[1] - WT_BAR_FILL_A[1]) * t)
            b = int(WT_BAR_FILL_A[2] + (WT_BAR_FILL_B[2] - WT_BAR_FILL_A[2]) * t)
            pygame.draw.line(panel, (r, g, b),
                             (bar_x + xi, bar_y + 1), (bar_x + xi, bar_y + bar_h - 2))
    sheen = pygame.Surface((bar_w, bar_h // 2), pygame.SRCALPHA)
    for yi in range(bar_h // 2):
        a = int(50 * (1 - yi / (bar_h // 2)))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, yi), (bar_w, yi))
    panel.blit(sheen, (bar_x, bar_y))
    pygame.draw.rect(panel, (20, 60, 120, 180), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=11)
    pct_s = font_ft_hint.render(f"{int(wt_progress * 100)}%", True, WOOD_BROWN)
    panel.blit(pct_s, (bar_x + bar_w + 6, bar_y + bar_h // 2 - pct_s.get_height() // 2))
    hint_s = font_ft_body.render("Click the PUMP button as fast as you can!", True, (40, 70, 130))
    panel.blit(hint_s, (PW // 2 - hint_s.get_width() // 2, 100))
    drain_s = font_ft_hint.render("(water drains if you stop — keep clicking!)", True, (120, 85, 40))
    panel.blit(drain_s, (PW // 2 - drain_s.get_width() // 2, 122))
    bowl_cx    = PW // 2
    bowl_top_y = int(PH * 0.52)
    bowl_bot_y = int(PH * 0.72)
    bowl_top_hw = 72
    bowl_bot_hw = 44
    bowl_depth  = bowl_bot_y - bowl_top_y
    rim_l  = bowl_cx - bowl_top_hw
    rim_r  = bowl_cx + bowl_top_hw
    base_l = bowl_cx - bowl_bot_hw
    base_r = bowl_cx + bowl_bot_hw
    fill_frac = min(wt_progress, 1.0)
    water_h   = int(bowl_depth * fill_frac)
    if water_h > 1:
        water_y      = bowl_bot_y - water_h
        t_surface    = 1.0 - (water_y - bowl_top_y) / max(bowl_depth, 1)
        hw_at_surface = bowl_bot_hw + (bowl_top_hw - bowl_bot_hw) * t_surface
        wave_off = int(math.sin(wt_wave_t * 3.8) * 4)
        water_poly = [
            (bowl_cx - hw_at_surface, water_y + wave_off),
            (bowl_cx + hw_at_surface, water_y - wave_off),
            (base_r, bowl_bot_y),
            (base_l, bowl_bot_y),
        ]
        water_surf = pygame.Surface((PW, PH), pygame.SRCALPHA)
        pygame.draw.polygon(water_surf, (*WT_WATER_BLUE, 210), water_poly)
        shimmer_h = 10
        shimmer_poly = [
            (bowl_cx - hw_at_surface, water_y + wave_off),
            (bowl_cx + hw_at_surface, water_y - wave_off),
            (bowl_cx + hw_at_surface, water_y - wave_off + shimmer_h),
            (bowl_cx - hw_at_surface, water_y + wave_off + shimmer_h),
        ]
        pygame.draw.polygon(water_surf, (160, 220, 255, 120), shimmer_poly)
        panel.blit(water_surf, (0, 0))
    bowl_poly = [(rim_l, bowl_top_y), (rim_r, bowl_top_y),
                 (base_r, bowl_bot_y), (base_l, bowl_bot_y)]
    pygame.draw.polygon(panel, (210, 185, 140, 80), bowl_poly)
    pygame.draw.polygon(panel, WT_BOWL_RIM, bowl_poly, 4)
    rim_ry = 10
    pygame.draw.ellipse(panel, (230, 205, 160),
                        (rim_l, bowl_top_y - rim_ry, bowl_top_hw * 2, rim_ry * 2))
    pygame.draw.ellipse(panel, WT_BOWL_RIM,
                        (rim_l, bowl_top_y - rim_ry, bowl_top_hw * 2, rim_ry * 2), 3)
    pygame.draw.line(panel, (255, 240, 200, 160),
                     (rim_l + 10, bowl_top_y + 8),
                     (base_l + 6, bowl_bot_y - 4), 2)
    if wt_flash_t > 0:
        alpha = int(wt_flash_t / 0.18 * 65)
        flash = pygame.Surface((PW, PH), pygame.SRCALPHA)
        flash.fill((80, 180, 255, alpha))
        panel.blit(flash, (0, 0))
    if wt_progress >= 1.0:
        done_s  = font_ft_big.render("Bowl Filled!", True, WT_WATER_BLUE)
        done_sh = font_ft_big.render("Bowl Filled!", True, (0, 0, 0))
        done_sh.set_alpha(60)
        cx = PW // 2 - done_s.get_width() // 2
        cy = PH - 50
        panel.blit(done_sh, (cx + 2, cy + 2))
        panel.blit(done_s,  (cx, cy))
    btn_w  = 160
    btn_h  = 52
    btn_x  = PW // 2 - btn_w // 2
    btn_y  = int(PH * 0.835)
    squish = int(wt_btn_press_t / 0.12 * 5)
    b_col  = (55, 150, 240) if wt_btn_press_t <= 0 else (80, 180, 255)
    b_dark = (20, 85, 165)
    pygame.draw.rect(panel, b_dark,
                     (btn_x + 2, btn_y + 4 - squish, btn_w, btn_h + squish),
                     border_radius=btn_h // 2)
    pygame.draw.rect(panel, b_col,
                     (btn_x, btn_y, btn_w, btn_h - squish),
                     border_radius=btn_h // 2)
    hl = pygame.Surface((btn_w - 4, max(1, (btn_h - squish) // 2)), pygame.SRCALPHA)
    for hy in range(max(1, (btn_h - squish) // 2)):
        a = int(70 * (1 - hy / max(1, (btn_h - squish) // 2)))
        pygame.draw.line(hl, (255, 255, 255, a), (0, hy), (btn_w - 4, hy))
    panel.blit(hl, (btn_x + 2, btn_y + 2))
    pump_lbl = font_play.render("PUMP!", True, WHITE)
    pump_sh  = font_play.render("PUMP!", True, (0, 0, 0))
    pump_sh.set_alpha(55)
    lx = btn_x + btn_w // 2 - pump_lbl.get_width() // 2
    ly = btn_y + (btn_h - squish) // 2 - pump_lbl.get_height() // 2
    panel.blit(pump_sh, (lx + 1, ly + 1))
    panel.blit(pump_lbl, (lx, ly))
    scaled_panel = pygame.transform.smoothscale(panel, (int(PW * scale), int(PH * scale)))
    surf.blit(scaled_panel, (px, py))
    wt_btn_rect = pygame.Rect(
        px + int(btn_x * scale),
        py + int(btn_y * scale),
        int(btn_w * scale),
        int((btn_h - squish) * scale),
    )
    for rip in wt_ripples:
        rip.draw(surf)
    cs = 32
    wt_close_rect = pygame.Rect(px + int(PW * scale) - cs - 8, py + 8, cs, cs)
    close_hov = wt_close_rect.collidepoint(*pygame.mouse.get_pos())
    col = (210, 70, 50) if close_hov else (170, 50, 30)
    pygame.draw.circle(surf, col, wt_close_rect.center, wt_close_rect.w // 2)
    pygame.draw.circle(surf, (255, 255, 255), wt_close_rect.center, wt_close_rect.w // 2, 2)
    x_s = font_ft_body.render("X", True, WHITE)
    surf.blit(x_s, (wt_close_rect.centerx - x_s.get_width() // 2,
                    wt_close_rect.centery - x_s.get_height() // 2))
    draw_warning_overlay_on_top(surf)

# ══════════════════════════════════════════════════════════════════════════════
# ── Whack-a-Mole Task (Distract with Toys) ───────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
WM_PANEL_W       = 540
WM_PANEL_H       = 420
WM_HOLES         = 6
WM_HITS_TO_WIN   = 8
WM_TOY_SHOW_TIME = 1.2
WM_SPAWN_RATE    = 1.4
WM_MAX_ACTIVE    = 2

wm_active         = False
wm_progress       = 0.0
wm_hits           = 0
wm_anim_t         = 0.0
wm_close_rect     = pygame.Rect(0, 0, 0, 0)
wm_flash_t        = 0.0
wm_miss_flash_t   = 0.0
wm_spawn_timer    = 0.0
wm_toys           = []
wm_hole_rects     = []
wm_bonk_particles = []

class _BonkParticle:
    def __init__(self, x, y):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(60, 160)
        self.x  = float(x)
        self.y  = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 80
        self.life  = 1.0
        self.decay = random.uniform(2.0, 3.2)
        self.r  = random.randint(4, 9)
        self.col = random.choice([(255,220,60),(255,160,40),(255,100,60)])

    def update(self, dt):
        self.vy  += 300 * dt
        self.x   += self.vx * dt
        self.y   += self.vy * dt
        self.life -= self.decay * dt
        return self.life > 0

    def draw(self, surf):
        alpha = int(max(0, self.life) * 255)
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.gfxdraw.filled_circle(s, self.r, self.r, self.r, (*self.col, alpha))
        surf.blit(s, (int(self.x)-self.r, int(self.y)-self.r))

def wm_open():
    global wm_active, wm_progress, wm_hits, wm_anim_t
    global wm_flash_t, wm_miss_flash_t, wm_spawn_timer
    global wm_toys, wm_bonk_particles
    wm_active         = True
    wm_progress       = 0.0
    wm_hits           = 0
    wm_anim_t         = 0.0
    wm_flash_t        = 0.0
    wm_miss_flash_t   = 0.0
    wm_spawn_timer    = 0.6
    wm_toys           = []
    wm_bonk_particles = []

def _wm_hole_centres(px, py, scale):
    PW = WM_PANEL_W
    PH = WM_PANEL_H
    cols, rows = 3, 2
    margin_x = int(PW * 0.18)
    margin_y = int(PH * 0.38)
    spacing_x = (PW - margin_x * 2) // (cols - 1)
    spacing_y = int(PH * 0.22)
    centres = []
    for row in range(rows):
        for col in range(cols):
            lx = margin_x + col * spacing_x
            ly = margin_y + row * spacing_y
            cx = px + int(lx * scale)
            cy = py + int(ly * scale)
            centres.append((cx, cy))
    return centres

def wm_update(events, dt):
    global wm_active, wm_progress, wm_hits, wm_anim_t
    global wm_flash_t, wm_miss_flash_t, wm_spawn_timer
    global wm_toys, wm_bonk_particles, wm_close_rect, wm_hole_rects
    if not wm_active:
        return False, False
    if wm_anim_t < 1.0:
        wm_anim_t = min(1.0, wm_anim_t + dt * 4.5)
    wm_flash_t      = max(0.0, wm_flash_t      - dt)
    wm_miss_flash_t = max(0.0, wm_miss_flash_t - dt)
    for toy in wm_toys:
        if not toy["hit"]:
            toy["show_t"] -= dt
        toy["squish_t"] = max(0.0, toy["squish_t"] - dt)
    wm_toys = [t for t in wm_toys if t["show_t"] > 0 or t["hit"]]
    wm_toys = [t for t in wm_toys if not (t["hit"] and t["squish_t"] <= 0)]
    wm_bonk_particles[:] = [p for p in wm_bonk_particles if p.update(dt)]
    active_count  = sum(1 for t in wm_toys if not t["hit"])
    speed_factor  = max(0.6, 1.0 - wm_hits * 0.03)
    spawn_interval = WM_SPAWN_RATE * speed_factor
    if active_count < WM_MAX_ACTIVE:
        wm_spawn_timer -= dt
        if wm_spawn_timer <= 0:
            used_holes = {t["hole"] for t in wm_toys}
            available  = [h for h in range(WM_HOLES) if h not in used_holes]
            if available:
                hole = random.choice(available)
                show_time = WM_TOY_SHOW_TIME * speed_factor
                wm_toys.append({
                    "hole":     hole,
                    "show_t":   show_time,
                    "max_show": show_time,
                    "hit":      False,
                    "squish_t": 0.0,
                })
            wm_spawn_timer = spawn_interval
    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            wm_active = False
            return False, True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if wm_close_rect.collidepoint(mx, my):
                play_sound(sfx_click)
                wm_active = False
                return False, True
            hit_something = False
            for toy in wm_toys:
                if toy["hit"]:
                    continue
                hole_idx = toy["hole"]
                if hole_idx < len(wm_hole_rects):
                    hr = wm_hole_rects[hole_idx]
                    if hr.collidepoint(mx, my):
                        toy["hit"]      = True
                        toy["squish_t"] = 0.35
                        wm_hits        += 1
                        wm_progress     = min(1.0, wm_hits / WM_HITS_TO_WIN)
                        wm_flash_t      = 0.25
                        hit_something   = True
                        for _ in range(random.randint(8, 14)):
                            wm_bonk_particles.append(_BonkParticle(mx, my))
                        play_sound(sfx_click)
                        break
            if not hit_something:
                wm_miss_flash_t = 0.18
    if wm_progress >= 1.0:
        play_sound(sfx_task_complete)
        wm_active = False
        return True, False
    return False, False

def wm_draw(surf):
    global wm_close_rect, wm_hole_rects
    if not wm_active:
        return
    PW    = WM_PANEL_W
    PH    = WM_PANEL_H
    scale = 0.55 + 0.45 * (1 - (1 - wm_anim_t) ** 3)
    px = (SCREEN_W - int(PW * scale)) // 2
    py = (SCREEN_H - int(PH * scale)) // 2
    dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, int(165 * wm_anim_t)))
    surf.blit(dim, (0, 0))
    panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*WM_BG, 248), (0, 0, PW, PH), border_radius=20)
    pygame.draw.rect(panel, (*WM_HOLE_RIM, 255), (0, 0, PW, PH), 3, border_radius=20)
    banner_h = 54
    pygame.draw.rect(panel, (*WM_BANNER, 240), (0, 0, PW, banner_h), border_radius=20)
    pygame.draw.rect(panel, (*WM_BANNER, 240), (0, banner_h//2, PW, banner_h//2))
    title_s = font_ft_title.render("Distract with Toys!", True, (255, 210, 100))
    panel.blit(title_s, (PW//2 - title_s.get_width()//2,
                          banner_h//2 - title_s.get_height()//2))
    bar_x, bar_y = 60, 68
    bar_w, bar_h = PW - 120, 20
    pygame.draw.rect(panel, (30, 18, 8), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
    fill_w = int(bar_w * wm_progress)
    if fill_w > 0:
        for xi in range(fill_w):
            t = xi / max(bar_w, 1)
            r = int(WM_PROGRESS_A[0] + (WM_PROGRESS_B[0] - WM_PROGRESS_A[0]) * t)
            g = int(WM_PROGRESS_A[1] + (WM_PROGRESS_B[1] - WM_PROGRESS_A[1]) * t)
            b = int(WM_PROGRESS_A[2] + (WM_PROGRESS_B[2] - WM_PROGRESS_A[2]) * t)
            pygame.draw.line(panel, (r, g, b),
                             (bar_x+xi, bar_y+1), (bar_x+xi, bar_y+bar_h-2))
    pygame.draw.rect(panel, (*WM_HOLE_RIM, 180), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)
    hits_lbl = font_ft_hint.render(f"{wm_hits} / {WM_HITS_TO_WIN} hits", True, (255, 200, 80))
    panel.blit(hits_lbl, (bar_x + bar_w + 6, bar_y + bar_h//2 - hits_lbl.get_height()//2))
    hint_s = font_ft_body.render("Click the toys before they hide!", True, (220, 180, 100))
    panel.blit(hint_s, (PW//2 - hint_s.get_width()//2, 96))
    cols, rows = 3, 2
    margin_x   = int(PW * 0.18)
    margin_y   = int(PH * 0.38)
    spacing_x  = (PW - margin_x * 2) // (cols - 1)
    spacing_y  = int(PH * 0.22)
    hole_r     = 36
    local_hole_centres = []
    for row in range(rows):
        for col in range(cols):
            lx = margin_x + col * spacing_x
            ly = margin_y + row * spacing_y
            local_hole_centres.append((lx, ly))
    for lx, ly in local_hole_centres:
        pygame.draw.ellipse(panel, WM_HOLE_COL,
                            (lx - hole_r, ly - hole_r//2, hole_r*2, hole_r))
        pygame.draw.ellipse(panel, WM_HOLE_RIM,
                            (lx - hole_r, ly - hole_r//2, hole_r*2, hole_r), 3)
    for toy in wm_toys:
        lx, ly = local_hole_centres[toy["hole"]]
        frac     = 1.0 - (toy["show_t"] / toy["max_show"])
        pop_frac = min(1.0, frac * 4)
        toy_h  = int(hole_r * 1.6 * pop_frac)
        squish = int(toy["squish_t"] / 0.35 * 10) if toy["hit"] else 0
        toy_w  = hole_r + squish
        toy_h  = max(4, toy_h - squish)
        col = WM_TOY_LIT if toy["hit"] else WM_TOY_COL
        toy_rect = pygame.Rect(lx - toy_w//2, ly - toy_h, toy_w, toy_h)
        if toy_h > 0:
            pygame.draw.rect(panel, col, toy_rect, border_radius=12)
            eye_y = toy_rect.top + toy_h//3
            if toy["hit"]:
                for ex in [lx - 8, lx + 8]:
                    pygame.draw.line(panel, (60,20,10), (ex-4, eye_y-4), (ex+4, eye_y+4), 3)
                    pygame.draw.line(panel, (60,20,10), (ex+4, eye_y-4), (ex-4, eye_y+4), 3)
            else:
                pygame.gfxdraw.filled_circle(panel, lx-8, eye_y, 4, (60,20,10,230))
                pygame.gfxdraw.filled_circle(panel, lx+8, eye_y, 4, (60,20,10,230))
            star_s = font_ft_hint.render("★", True, (255,240,120))
            panel.blit(star_s, (lx - star_s.get_width()//2, toy_rect.top + 2))
    if wm_flash_t > 0:
        alpha = int(wm_flash_t / 0.25 * 80)
        fl = pygame.Surface((PW, PH), pygame.SRCALPHA)
        fl.fill((255, 210, 60, alpha))
        panel.blit(fl, (0, 0))
    if wm_miss_flash_t > 0:
        alpha = int(wm_miss_flash_t / 0.18 * 60)
        fl = pygame.Surface((PW, PH), pygame.SRCALPHA)
        fl.fill((200, 50, 30, alpha))
        panel.blit(fl, (0, 0))
    scaled_panel = pygame.transform.smoothscale(panel, (int(PW*scale), int(PH*scale)))
    surf.blit(scaled_panel, (px, py))
    hole_centres_screen = _wm_hole_centres(px, py, scale)
    wm_hole_rects = []
    for scx, scy in hole_centres_screen:
        hr = int(hole_r * scale)
        wm_hole_rects.append(pygame.Rect(scx - hr, scy - hr*2, hr*2, hr*2))
    for p in wm_bonk_particles:
        p.draw(surf)
    cs = 32
    wm_close_rect = pygame.Rect(px + int(PW*scale) - cs - 8, py + 8, cs, cs)
    close_hov = wm_close_rect.collidepoint(*pygame.mouse.get_pos())
    col = (210, 70, 50) if close_hov else (170, 50, 30)
    pygame.draw.circle(surf, col, wm_close_rect.center, wm_close_rect.w//2)
    pygame.draw.circle(surf, (255,255,255), wm_close_rect.center, wm_close_rect.w//2, 2)
    x_s = font_ft_body.render("X", True, WHITE)
    surf.blit(x_s, (wm_close_rect.centerx - x_s.get_width()//2,
                    wm_close_rect.centery - x_s.get_height()//2))
    draw_warning_overlay_on_top(surf)

# ══════════════════════════════════════════════════════════════════════════════
# ── Simon Says Task (Calm Your Pet) ──────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
SS_PANEL_W = 560
SS_PANEL_H = 440
SS_DIRS       = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
SS_DIR_LABELS = ["UP", "DOWN", "LEFT", "RIGHT"]
SS_DIR_ARROWS = ["↑", "↓", "←", "→"]
SS_DIR_COLS   = [SS_BTN_UP, SS_BTN_DOWN, SS_BTN_LEFT, SS_BTN_RIGHT]
SS_DIR_LIT    = [SS_BTN_LIT_UP, SS_BTN_LIT_DOWN, SS_BTN_LIT_LEFT, SS_BTN_LIT_RIGHT]

ss_active         = False
ss_anim_t         = 0.0
ss_close_rect     = pygame.Rect(0, 0, 0, 0)
ss_phase          = "idle"
ss_sequence       = []
ss_show_index     = 0
ss_input_index    = 0
ss_flash_t        = 0.0
ss_pause_t        = 0.0
ss_wrong_t        = 0.0
ss_success_t      = 0.0
ss_progress       = 0.0
ss_round          = 0
ss_noise_level    = 0.0
ss_lit_button     = -1
ss_result_t       = 0.0
ss_input_timer    = 0.0

SS_ROUNDS_TO_WIN   = 4
SS_FLASH_ON_TIME   = 0.25
SS_FLASH_OFF_TIME  = 0.11
SS_NOISE_PER_WRONG = 0.35
SS_NOISE_DRAIN     = 0.08
SS_INPUT_TIMEOUT   = 3.0

def ss_open():
    global ss_active, ss_anim_t, ss_phase, ss_sequence, ss_show_index
    global ss_input_index, ss_flash_t, ss_pause_t, ss_wrong_t, ss_success_t
    global ss_progress, ss_round, ss_noise_level, ss_lit_button
    global ss_result_t, ss_input_timer
    ss_active       = True
    ss_anim_t       = 0.0
    ss_phase        = "idle"
    ss_sequence     = []
    ss_show_index   = 0
    ss_input_index  = 0
    ss_flash_t      = 0.0
    ss_pause_t      = 0.0
    ss_wrong_t      = 0.0
    ss_success_t    = 0.0
    ss_progress     = 0.0
    ss_round        = 0
    ss_noise_level  = 0.0
    ss_lit_button   = -1
    ss_result_t     = 0.0
    ss_input_timer  = 0.0
    _ss_next_round()

def _ss_next_round():
    global ss_phase, ss_sequence, ss_show_index, ss_input_index
    global ss_flash_t, ss_pause_t, ss_lit_button, ss_round
    ss_round      += 1
    ss_sequence.append(random.randint(0, 3))
    ss_show_index  = 0
    ss_input_index = 0
    ss_lit_button  = -1
    ss_flash_t     = 0.0
    ss_pause_t     = 0.28
    ss_phase       = "showing"

def ss_update(events, dt):
    global ss_active, ss_anim_t, ss_phase, ss_sequence, ss_show_index
    global ss_input_index, ss_flash_t, ss_pause_t, ss_wrong_t, ss_success_t
    global ss_progress, ss_noise_level, ss_lit_button, ss_result_t, ss_input_timer
    if not ss_active:
        return False, False
    if ss_anim_t < 1.0:
        ss_anim_t = min(1.0, ss_anim_t + dt * 4.5)
    ss_noise_level = max(0.0, ss_noise_level - SS_NOISE_DRAIN * dt)
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            ss_active = False
            return False, True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx2, my2 = pygame.mouse.get_pos()
            if ss_close_rect.collidepoint(mx2, my2):
                play_sound(sfx_click)
                ss_active = False
                return False, True
    if ss_phase == "showing":
        if ss_pause_t > 0:
            ss_pause_t -= dt
            ss_lit_button = -1
        else:
            if ss_flash_t <= 0:
                if ss_show_index < len(ss_sequence):
                    ss_lit_button = ss_sequence[ss_show_index]
                    ss_flash_t    = SS_FLASH_ON_TIME
                else:
                    ss_lit_button  = -1
                    ss_phase       = "input"
                    ss_input_index = 0
                    ss_input_timer = SS_INPUT_TIMEOUT
            else:
                ss_flash_t -= dt
                if ss_flash_t <= 0:
                    ss_lit_button  = -1
                    ss_show_index += 1
                    ss_pause_t     = SS_FLASH_OFF_TIME
    elif ss_phase == "input":
        ss_input_timer -= dt
        if ss_input_timer <= 0:
            ss_wrong_t     = 0.55
            ss_noise_level = min(1.0, ss_noise_level + SS_NOISE_PER_WRONG)
            ss_phase       = "wrong"
            ss_input_timer = 0.0
        for event in events:
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key in SS_DIRS:
                    pressed_dir = SS_DIRS.index(key)
                    ss_lit_button = pressed_dir
                    play_sound(sfx_click)
                    if pressed_dir == ss_sequence[ss_input_index]:
                        ss_input_index += 1
                        if ss_input_index >= len(ss_sequence):
                            ss_progress   = min(1.0, ss_round / SS_ROUNDS_TO_WIN)
                            ss_success_t  = 0.6
                            ss_phase      = "success"
                            ss_result_t   = 1.1
                            ss_lit_button = -1
                    else:
                        ss_noise_level = min(1.0, ss_noise_level + SS_NOISE_PER_WRONG)
                        ss_wrong_t     = 0.55
                        ss_phase       = "wrong"
                        ss_lit_button  = -1
    elif ss_phase == "wrong":
        ss_wrong_t -= dt
        if ss_wrong_t <= 0:
            ss_show_index  = 0
            ss_input_index = 0
            ss_flash_t     = 0.0
            ss_pause_t     = 0.45
            ss_phase       = "showing"
    elif ss_phase == "success":
        ss_success_t -= dt
        ss_result_t  -= dt
        if ss_result_t <= 0:
            if ss_progress >= 1.0:
                play_sound(sfx_task_complete)
                ss_active = False
                return True, False
            else:
                _ss_next_round()
    return False, False

def ss_draw(surf):
    global ss_close_rect
    if not ss_active:
        return
    PW    = SS_PANEL_W
    PH    = SS_PANEL_H
    scale = 0.55 + 0.45 * (1 - (1 - ss_anim_t) ** 3)
    px = (SCREEN_W - int(PW * scale)) // 2
    py = (SCREEN_H - int(PH * scale)) // 2
    dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, int(165 * ss_anim_t)))
    surf.blit(dim, (0, 0))
    panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*SS_BG, 248), (0, 0, PW, PH), border_radius=22)
    pygame.draw.rect(panel, (130, 80, 180, 255), (0, 0, PW, PH), 3, border_radius=22)
    banner_h = 54
    pygame.draw.rect(panel, (*SS_BANNER, 240), (0, 0, PW, banner_h), border_radius=22)
    pygame.draw.rect(panel, (*SS_BANNER, 240), (0, banner_h // 2, PW, banner_h // 2))
    title_s = font_ft_title.render("Calm Your Pet!", True, (220, 190, 255))
    panel.blit(title_s, (PW // 2 - title_s.get_width() // 2,
                          banner_h // 2 - title_s.get_height() // 2))
    bar_x, bar_y = 55, 68
    bar_w, bar_h = PW - 110, 20
    pygame.draw.rect(panel, SS_PROGRESS_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=10)
    fill_w = int(bar_w * ss_progress)
    if fill_w > 0:
        for xi in range(fill_w):
            t = xi / max(bar_w, 1)
            r = int(SS_PROGRESS_FILL_A[0] + (SS_PROGRESS_FILL_B[0] - SS_PROGRESS_FILL_A[0]) * t)
            g = int(SS_PROGRESS_FILL_A[1] + (SS_PROGRESS_FILL_B[1] - SS_PROGRESS_FILL_A[1]) * t)
            b = int(SS_PROGRESS_FILL_A[2] + (SS_PROGRESS_FILL_B[2] - SS_PROGRESS_FILL_A[2]) * t)
            pygame.draw.line(panel, (r, g, b),
                             (bar_x + xi, bar_y + 1), (bar_x + xi, bar_y + bar_h - 2))
    sheen = pygame.Surface((bar_w, bar_h // 2), pygame.SRCALPHA)
    for yi in range(bar_h // 2):
        a = int(40 * (1 - yi / (bar_h // 2)))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, yi), (bar_w, yi))
    panel.blit(sheen, (bar_x, bar_y))
    pygame.draw.rect(panel, (100, 60, 160, 180), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)
    calm_lbl = font_ft_hint.render(f"Calm  {int(ss_progress * 100)}%", True, (200, 170, 255))
    panel.blit(calm_lbl, (bar_x + bar_w + 6, bar_y + bar_h // 2 - calm_lbl.get_height() // 2))
    nm_x, nm_y = 55, 96
    nm_w, nm_h = PW - 110, 14
    pygame.draw.rect(panel, SS_NOISE_BG, (nm_x, nm_y, nm_w, nm_h), border_radius=7)
    noise_fill_w = int(nm_w * ss_noise_level)
    if noise_fill_w > 0:
        noise_col = (
            int(SS_NOISE_SAFE[0] + (SS_NOISE_FILL[0] - SS_NOISE_SAFE[0]) * ss_noise_level),
            int(SS_NOISE_SAFE[1] + (SS_NOISE_FILL[1] - SS_NOISE_SAFE[1]) * ss_noise_level),
            int(SS_NOISE_SAFE[2] + (SS_NOISE_FILL[2] - SS_NOISE_SAFE[2]) * ss_noise_level),
        )
        pygame.draw.rect(panel, noise_col, (nm_x, nm_y, noise_fill_w, nm_h), border_radius=7)
    pygame.draw.rect(panel, (120, 40, 40, 150), (nm_x, nm_y, nm_w, nm_h), 2, border_radius=7)
    noise_lbl = font_ft_hint.render("Noise", True, (220, 140, 140))
    panel.blit(noise_lbl, (nm_x + nm_w + 6, nm_y + nm_h // 2 - noise_lbl.get_height() // 2))
    if ss_phase == "showing":
        hint_text = "Watch carefully..."
        hint_col  = (200, 180, 255)
    elif ss_phase == "input":
        remaining = max(0, int(ss_input_timer) + 1)
        hint_text = f"Your turn! Repeat the pattern  ({remaining}s)"
        hint_col  = (180, 255, 200)
    elif ss_phase == "wrong":
        hint_text = "Too loud! Watch again..."
        hint_col  = (255, 140, 130)
    elif ss_phase == "success":
        hint_text = "Good job! Pet is calmer!"
        hint_col  = (180, 255, 160)
    else:
        hint_text = ""
        hint_col  = WHITE
    hint_s = font_ft_body.render(hint_text, True, hint_col)
    panel.blit(hint_s, (PW // 2 - hint_s.get_width() // 2, 118))
    round_s = font_ft_hint.render(f"Round {ss_round} / {SS_ROUNDS_TO_WIN}", True, (160, 140, 200))
    panel.blit(round_s, (PW // 2 - round_s.get_width() // 2, 140))
    btn_r   = 44
    ctr_x   = PW // 2
    ctr_y   = int(PH * 0.60)
    gap     = 14
    btn_centres = [
        (ctr_x,          ctr_y - btn_r - gap),
        (ctr_x,          ctr_y + btn_r + gap),
        (ctr_x - btn_r*2 - gap, ctr_y),
        (ctr_x + btn_r*2 + gap, ctr_y),
    ]
    for di in range(4):
        bx_c, by_c = btn_centres[di]
        bx = bx_c - btn_r
        by = by_c - btn_r
        bw = btn_r * 2
        bh = btn_r * 2
        is_lit   = (ss_lit_button == di)
        is_wrong = (ss_phase == "wrong" and ss_wrong_t > 0)
        if is_wrong and ss_input_index > 0 and di == ss_sequence[ss_input_index - 1 if ss_input_index > 0 else 0]:
            col = (255, 80, 60)
        elif is_lit:
            col = SS_DIR_LIT[di]
        else:
            col = SS_DIR_COLS[di]
        dark = tuple(max(0, c - 60) for c in col)
        shadow_s = pygame.Surface((bw + 4, bh + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_s, (0, 0, 0, 70), (0, 0, bw + 4, bh + 6), border_radius=14)
        panel.blit(shadow_s, (bx - 2, by + 4))
        press_offset = 4 if is_lit else 0
        pygame.draw.rect(panel, dark, (bx + 2, by + 4, bw, bh), border_radius=14)
        pygame.draw.rect(panel, col,  (bx, by + press_offset, bw, bh - press_offset), border_radius=14)
        hl = pygame.Surface((bw - 4, (bh - press_offset) // 2), pygame.SRCALPHA)
        for hy in range(max(1, (bh - press_offset) // 2)):
            a = int(80 * (1 - hy / max(1, (bh - press_offset) // 2)))
            pygame.draw.line(hl, (255, 255, 255, a), (0, hy), (bw - 4, hy))
        panel.blit(hl, (bx + 2, by + 2 + press_offset))
        if is_lit:
            glow_s = pygame.Surface((bw + 20, bh + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_s, (*SS_DIR_LIT[di], 80), (0, 0, bw + 20, bh + 20), border_radius=18)
            panel.blit(glow_s, (bx - 10, by - 10))
        arrow_s  = font_ft_big.render(SS_DIR_ARROWS[di], True, WHITE)
        arrow_sh = font_ft_big.render(SS_DIR_ARROWS[di], True, (0, 0, 0))
        arrow_sh.set_alpha(60)
        ax = bx + bw // 2 - arrow_s.get_width() // 2
        ay = by + press_offset + (bh - press_offset) // 2 - arrow_s.get_height() // 2
        panel.blit(arrow_sh, (ax + 1, ay + 1))
        panel.blit(arrow_s,  (ax, ay))
    dot_y  = int(PH * 0.885)
    dot_r  = 7
    dot_gap = dot_r * 2 + 6
    total_dots = len(ss_sequence)
    dot_start_x = PW // 2 - (total_dots * (dot_r * 2 + 6) - 6) // 2
    for di in range(total_dots):
        dx = dot_start_x + di * dot_gap + dot_r
        if ss_phase == "input" and di < ss_input_index:
            dot_col = (120, 255, 140)
        elif ss_phase == "showing" and di < ss_show_index:
            dot_col = (200, 160, 255)
        else:
            dot_col = (70, 50, 100)
        pygame.gfxdraw.filled_circle(panel, dx, dot_y, dot_r, (*dot_col, 220))
        pygame.gfxdraw.aacircle(panel, dx, dot_y, dot_r, (150, 120, 200, 200))
    if ss_wrong_t > 0:
        alpha = int(ss_wrong_t / 0.55 * 100)
        err_s = pygame.Surface((PW, PH), pygame.SRCALPHA)
        err_s.fill((220, 50, 30, alpha))
        panel.blit(err_s, (0, 0))
    # ── Subtle green flash on round success — no banner text ──────────────────
    if ss_success_t > 0:
        alpha = int(ss_success_t / 0.6 * 60)
        ok_s  = pygame.Surface((PW, PH), pygame.SRCALPHA)
        ok_s.fill((80, 220, 100, alpha))
        panel.blit(ok_s, (0, 0))
    scaled_panel = pygame.transform.smoothscale(panel, (int(PW * scale), int(PH * scale)))
    surf.blit(scaled_panel, (px, py))
    cs = 32
    ss_close_rect = pygame.Rect(px + int(PW * scale) - cs - 8, py + 8, cs, cs)
    close_hov = ss_close_rect.collidepoint(*pygame.mouse.get_pos())
    col = (210, 70, 50) if close_hov else (170, 50, 30)
    pygame.draw.circle(surf, col, ss_close_rect.center, ss_close_rect.w // 2)
    pygame.draw.circle(surf, (255, 255, 255), ss_close_rect.center, ss_close_rect.w // 2, 2)
    x_s = font_ft_body.render("X", True, WHITE)
    surf.blit(x_s, (ss_close_rect.centerx - x_s.get_width() // 2,
                    ss_close_rect.centery - x_s.get_height() // 2))
    draw_warning_overlay_on_top(surf)

# ══════════════════════════════════════════════════════════════════════════════
# ── Cleanup Task (Clean Up Any Mess) — drag broom over dirt piles ─────────────
# ══════════════════════════════════════════════════════════════════════════════
CL_PANEL_W       = 560
CL_PANEL_H       = 430
CL_NUM_PILES     = 6
CL_SWEEP_RADIUS  = 48
CL_BROOM_SPEED   = 340

cl_active        = False
cl_progress      = 0.0
cl_anim_t        = 0.0
cl_close_rect    = pygame.Rect(0, 0, 0, 0)
cl_flash_t       = 0.0
cl_piles         = []
cl_broom_x       = 0.0
cl_broom_y       = 0.0
cl_sweeping      = False
cl_sparkles      = []
cl_panel_rect    = pygame.Rect(0, 0, 0, 0)


class _Sparkle:
    def __init__(self, x, y):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(40, 120)
        self.x     = float(x)
        self.y     = float(y)
        self.vx    = math.cos(angle) * speed
        self.vy    = math.sin(angle) * speed - 60
        self.life  = 1.0
        self.decay = random.uniform(1.8, 3.0)
        self.r     = random.randint(3, 7)
        self.col   = random.choice([CL_SPARKLE, (255, 255, 200), (200, 255, 180)])

    def update(self, dt):
        self.vy   += 200 * dt
        self.x    += self.vx * dt
        self.y    += self.vy * dt
        self.life -= self.decay * dt
        return self.life > 0

    def draw(self, surf):
        alpha = int(max(0, self.life) * 255)
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.gfxdraw.filled_circle(s, self.r, self.r, self.r, (*self.col, alpha))
        surf.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


def cl_open():
    global cl_active, cl_progress, cl_anim_t, cl_flash_t
    global cl_piles, cl_broom_x, cl_broom_y, cl_sweeping, cl_sparkles

    cl_active    = True
    cl_progress  = 0.0
    cl_anim_t    = 0.0
    cl_flash_t   = 0.0
    cl_sweeping  = False
    cl_sparkles  = []

    cl_piles = []
    fx1, fy1 = 70,  185
    fx2, fy2 = CL_PANEL_W - 70, CL_PANEL_H - 75
    placed = []
    attempts = 0
    while len(cl_piles) < CL_NUM_PILES and attempts < 500:
        attempts += 1
        nx = random.randint(fx1, fx2)
        ny = random.randint(fy1, fy2)
        too_close = any(math.hypot(nx - p["lx"], ny - p["ly"]) < 80 for p in placed)
        if not too_close:
            placed.append({"lx": nx, "ly": ny})
            cl_piles.append({
                "lx":      nx,
                "ly":      ny,
                "cleaned": False,
                "clean_t": 0.0,
                "wobble":  random.uniform(0, math.pi * 2),
                "size":    random.uniform(0.8, 1.3),
            })

    cl_broom_x = float(CL_PANEL_W // 2)
    cl_broom_y = float(CL_PANEL_H // 2)


def cl_update(events, dt):
    global cl_active, cl_progress, cl_anim_t, cl_flash_t
    global cl_piles, cl_broom_x, cl_broom_y, cl_sweeping, cl_sparkles
    global cl_close_rect, cl_panel_rect

    if not cl_active:
        return False, False

    if cl_anim_t < 1.0:
        cl_anim_t = min(1.0, cl_anim_t + dt * 4.5)

    cl_flash_t = max(0.0, cl_flash_t - dt)
    cl_sparkles[:] = [s for s in cl_sparkles if s.update(dt)]

    for pile in cl_piles:
        if pile["cleaned"]:
            pile["clean_t"] = min(1.0, pile["clean_t"] + dt * 4.0)
        pile["wobble"] += dt * 2.2

    mx, my = pygame.mouse.get_pos()

    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            cl_active = False
            return False, True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if cl_close_rect.collidepoint(mx, my):
                play_sound(sfx_click)
                cl_active = False
                return False, True
            if cl_panel_rect.collidepoint(mx, my):
                cl_sweeping = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            cl_sweeping = False

    if cl_sweeping and cl_panel_rect.collidepoint(mx, my):
        scale  = 0.55 + 0.45 * (1 - (1 - cl_anim_t) ** 3)
        local_mx = (mx - cl_panel_rect.x) / scale
        local_my = (my - cl_panel_rect.y) / scale

        dx = local_mx - cl_broom_x
        dy = local_my - cl_broom_y
        dist = math.hypot(dx, dy)
        move = CL_BROOM_SPEED * dt
        if dist > move:
            cl_broom_x += dx / dist * move
            cl_broom_y += dy / dist * move
        else:
            cl_broom_x = local_mx
            cl_broom_y = local_my

        for pile in cl_piles:
            if pile["cleaned"]:
                continue
            d = math.hypot(cl_broom_x - pile["lx"], cl_broom_y - pile["ly"])
            if d <= CL_SWEEP_RADIUS:
                pile["cleaned"] = True
                cl_flash_t = 0.28
                for _ in range(random.randint(6, 11)):
                    sx = cl_panel_rect.x + int(pile["lx"] * scale)
                    sy = cl_panel_rect.y + int(pile["ly"] * scale)
                    cl_sparkles.append(_Sparkle(sx, sy))
                play_sound(sfx_click)

    cleaned = sum(1 for p in cl_piles if p["cleaned"])
    cl_progress = cleaned / max(1, len(cl_piles))

    if cl_progress >= 1.0:
        play_sound(sfx_task_complete)
        cl_active = False
        return True, False

    return False, False


def cl_draw(surf):
    global cl_close_rect, cl_panel_rect

    if not cl_active:
        return

    PW    = CL_PANEL_W
    PH    = CL_PANEL_H
    scale = 0.55 + 0.45 * (1 - (1 - cl_anim_t) ** 3)

    pw_s = int(PW * scale)
    ph_s = int(PH * scale)
    px   = (SCREEN_W - pw_s) // 2
    py   = (SCREEN_H - ph_s) // 2
    cl_panel_rect = pygame.Rect(px, py, pw_s, ph_s)

    dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, int(165 * cl_anim_t)))
    surf.blit(dim, (0, 0))

    panel = pygame.Surface((PW, PH), pygame.SRCALPHA)

    pygame.draw.rect(panel, (*CL_BG, 248), (0, 0, PW, PH), border_radius=20)
    pygame.draw.rect(panel, (80, 120, 60, 255), (0, 0, PW, PH), 3, border_radius=20)

    banner_h = 54
    pygame.draw.rect(panel, (*CL_BANNER, 240), (0, 0, PW, banner_h), border_radius=20)
    pygame.draw.rect(panel, (*CL_BANNER, 240), (0, banner_h // 2, PW, banner_h // 2))
    title_s = font_ft_title.render("Clean Up the Mess!", True, (200, 240, 160))
    panel.blit(title_s, (PW // 2 - title_s.get_width() // 2,
                          banner_h // 2 - title_s.get_height() // 2))

    bar_x, bar_y = 60, 68
    bar_w, bar_h = PW - 120, 20
    pygame.draw.rect(panel, (15, 30, 12), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
    fill_w = int(bar_w * cl_progress)
    if fill_w > 0:
        for xi in range(fill_w):
            t = xi / max(bar_w, 1)
            r = int(CL_PROGRESS_A[0] + (CL_PROGRESS_B[0] - CL_PROGRESS_A[0]) * t)
            g = int(CL_PROGRESS_A[1] + (CL_PROGRESS_B[1] - CL_PROGRESS_A[1]) * t)
            b = int(CL_PROGRESS_A[2] + (CL_PROGRESS_B[2] - CL_PROGRESS_A[2]) * t)
            pygame.draw.line(panel, (r, g, b),
                             (bar_x + xi, bar_y + 1), (bar_x + xi, bar_y + bar_h - 2))
    sheen = pygame.Surface((bar_w, bar_h // 2), pygame.SRCALPHA)
    for yi in range(bar_h // 2):
        a = int(40 * (1 - yi / (bar_h // 2)))
        pygame.draw.line(sheen, (255, 255, 255, a), (0, yi), (bar_w, yi))
    panel.blit(sheen, (bar_x, bar_y))
    pygame.draw.rect(panel, (50, 100, 35, 160), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)

    cleaned_count = sum(1 for p in cl_piles if p["cleaned"])
    pct_s = font_ft_hint.render(f"{cleaned_count}/{len(cl_piles)}", True, (160, 220, 100))
    panel.blit(pct_s, (bar_x + bar_w + 6, bar_y + bar_h // 2 - pct_s.get_height() // 2))

    hint_s = font_ft_body.render("Hold & drag the broom over every dirt pile!", True, (160, 220, 120))
    panel.blit(hint_s, (PW // 2 - hint_s.get_width() // 2, 96))

    floor_rect = pygame.Rect(30, 160, PW - 60, PH - 200)
    pygame.draw.rect(panel, CL_FLOOR, floor_rect, border_radius=10)
    for fy_line in range(floor_rect.top + 28, floor_rect.bottom, 28):
        pygame.draw.line(panel, CL_FLOOR_DARK,
                         (floor_rect.left + 4, fy_line),
                         (floor_rect.right - 4, fy_line), 1)
    for fxi in range(floor_rect.left + 80, floor_rect.right, 80):
        pygame.draw.line(panel, CL_FLOOR_DARK,
                         (fxi, floor_rect.top + 4),
                         (fxi, floor_rect.bottom - 4), 1)
    pygame.draw.rect(panel, CL_FLOOR_DARK, floor_rect, 2, border_radius=10)

    for pile in cl_piles:
        lx, ly = pile["lx"], pile["ly"]
        wobble  = math.sin(pile["wobble"]) * 2
        sz      = pile["size"]

        if pile["cleaned"]:
            t   = pile["clean_t"]
            alpha_v = int(255 * (1 - t))
            scale_v = 1.0 - t * 0.8
            if alpha_v <= 0:
                continue
            pile_surf = pygame.Surface((int(60 * sz * scale_v) + 2,
                                        int(28 * sz * scale_v) + 2), pygame.SRCALPHA)
            pw2 = pile_surf.get_width()
            ph2 = pile_surf.get_height()
            pygame.draw.ellipse(pile_surf, (*CL_DIRT_COL, alpha_v), (0, 0, pw2, ph2))
            pygame.draw.ellipse(pile_surf, (*CL_DIRT_DARK, alpha_v), (0, 0, pw2, ph2), 2)
            panel.blit(pile_surf, (int(lx - pw2 // 2), int(ly - ph2 // 2)))
        else:
            pulse = abs(math.sin(pile["wobble"] * 0.7)) * 0.15 + 0.9
            pw2 = int(58 * sz * pulse)
            ph2 = int(26 * sz * pulse)
            pile_surf = pygame.Surface((pw2 + 4, ph2 + 4), pygame.SRCALPHA)
            pygame.draw.ellipse(pile_surf, (*CL_DIRT_COL, 230), (0, 0, pw2, ph2))
            for di in range(3):
                cx2 = int(pw2 * (0.25 + di * 0.25))
                cy2 = ph2 // 2
                cr2 = random.randint(4, 8) if di == 0 else int(pw2 * 0.10)
                pygame.gfxdraw.filled_circle(pile_surf, cx2, cy2, max(2, cr2),
                                             (*CL_DIRT_DARK, 180))
            pygame.draw.ellipse(pile_surf, (*CL_DIRT_DARK, 200), (0, 0, pw2, ph2), 2)
            panel.blit(pile_surf, (int(lx - pw2 // 2 + wobble), int(ly - ph2 // 2)))

            ring_alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.002 + pile["wobble"])) * 60 + 20)
            ring_r = int(CL_SWEEP_RADIUS * 0.75)
            ring_s = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
            pygame.gfxdraw.aacircle(ring_s, ring_r + 2, ring_r + 2, ring_r,
                                    (200, 240, 140, ring_alpha))
            panel.blit(ring_s, (lx - ring_r - 2, ly - ring_r - 2))

    bx, by = int(cl_broom_x), int(cl_broom_y)

    broom_angle = 0.0
    if cl_sweeping:
        broom_angle = math.sin(pygame.time.get_ticks() * 0.008) * 12

    handle_len = 70
    handle_angle_rad = math.radians(-60 + broom_angle)
    hx2 = bx + int(math.cos(handle_angle_rad) * handle_len)
    hy2 = by + int(math.sin(handle_angle_rad) * handle_len)
    pygame.draw.line(panel, CL_BROOM_HDL, (bx, by), (hx2, hy2), 7)
    pygame.draw.circle(panel, (120, 75, 25), (hx2, hy2), 5)

    head_w  = 52
    head_h  = 18
    head_angle = handle_angle_rad + math.pi / 2
    hcx = bx + int(math.cos(handle_angle_rad + math.pi) * 8)
    hcy = by + int(math.sin(handle_angle_rad + math.pi) * 8)
    cos_h = math.cos(head_angle)
    sin_h = math.sin(head_angle)
    head_pts = [
        (hcx + int(cos_h * head_w // 2),              hcy + int(sin_h * head_w // 2)),
        (hcx - int(cos_h * head_w // 2),              hcy - int(sin_h * head_w // 2)),
        (hcx - int(cos_h * (head_w // 2 - 6)) + int(math.cos(handle_angle_rad) * head_h),
         hcy - int(sin_h * (head_w // 2 - 6)) + int(math.sin(handle_angle_rad) * head_h)),
        (hcx + int(cos_h * (head_w // 2 - 6)) + int(math.cos(handle_angle_rad) * head_h),
         hcy + int(sin_h * (head_w // 2 - 6)) + int(math.sin(handle_angle_rad) * head_h)),
    ]
    if len(head_pts) >= 3:
        pygame.draw.polygon(panel, CL_BROOM_HEAD, head_pts)
        pygame.draw.polygon(panel, (160, 130, 60), head_pts, 2)

    for bi in range(7):
        t_b  = bi / 6
        bsx = int(hcx + cos_h * (head_w // 2 - head_w * t_b))
        bsy = int(hcy + sin_h * (head_w // 2 - head_w * t_b))
        bend = math.sin(pygame.time.get_ticks() * 0.01 + bi) * 4 if cl_sweeping else 0
        pygame.draw.line(panel, (140, 100, 40),
                         (bsx, bsy),
                         (bsx + int(math.cos(handle_angle_rad + math.pi) * 14 + bend),
                          bsy + int(math.sin(handle_angle_rad + math.pi) * 14 + bend)), 2)

    if cl_flash_t > 0:
        alpha = int(cl_flash_t / 0.28 * 75)
        fl = pygame.Surface((PW, PH), pygame.SRCALPHA)
        fl.fill((180, 255, 120, alpha))
        panel.blit(fl, (0, 0))

    if cl_progress >= 1.0:
        done_s  = font_ft_big.render("All Clean!", True, (140, 255, 120))
        done_sh = font_ft_big.render("All Clean!", True, (0, 0, 0))
        done_sh.set_alpha(60)
        cx = PW // 2 - done_s.get_width() // 2
        cy = PH - 52
        panel.blit(done_sh, (cx + 2, cy + 2))
        panel.blit(done_s,  (cx, cy))

    if not cl_sweeping:
        sw_hint = font_ft_hint.render("Hold left mouse button and drag to sweep!", True, (140, 200, 100))
        panel.blit(sw_hint, (PW // 2 - sw_hint.get_width() // 2, PH - 30))

    scaled_panel = pygame.transform.smoothscale(panel, (pw_s, ph_s))
    surf.blit(scaled_panel, (px, py))

    for sp in cl_sparkles:
        sp.draw(surf)

    cs = 32
    cl_close_rect = pygame.Rect(px + pw_s - cs - 8, py + 8, cs, cs)
    close_hov = cl_close_rect.collidepoint(*pygame.mouse.get_pos())
    col = (210, 70, 50) if close_hov else (170, 50, 30)
    pygame.draw.circle(surf, col, cl_close_rect.center, cl_close_rect.w // 2)
    pygame.draw.circle(surf, (255, 255, 255), cl_close_rect.center, cl_close_rect.w // 2, 2)
    x_s = font_ft_body.render("X", True, WHITE)
    surf.blit(x_s, (cl_close_rect.centerx - x_s.get_width() // 2,
                    cl_close_rect.centery - x_s.get_height() // 2))

    draw_warning_overlay_on_top(surf)

# ══════════════════════════════════════════════════════════════════════════════
# ── Task popup (generic fallback) ────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def draw_task_popup(surf, task_idx, anim_t):
    fw = task_frame_img.get_width()
    fh = task_frame_img.get_height()
    dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    dim.fill((0, 0, 0, int(160 * min(anim_t * 2, 1))))
    surf.blit(dim, (0, 0))
    scale = 0.6 + 0.4 * anim_t
    dw    = int(fw * scale)
    dh    = int(fh * scale)
    dx    = SCREEN_W // 2 - dw // 2
    dy    = SCREEN_H // 2 - dh // 2
    frame_surf = pygame.Surface((fw, fh), pygame.SRCALPHA)
    frame_surf.blit(task_frame_img, (0, 0))
    scaled = pygame.transform.smoothscale(frame_surf, (dw, dh))
    surf.blit(scaled, (dx, dy))
    cs      = 34
    close_x = dx + dw - cs // 2 - 6
    close_y = dy + cs // 2 + 6
    close_rect_tp = pygame.Rect(close_x - cs // 2, close_y - cs // 2, cs, cs)
    close_hov = close_rect_tp.collidepoint(*pygame.mouse.get_pos())
    col  = (220, 60, 45) if close_hov else (175, 40, 30)
    dark = (120, 20, 10)
    pygame.draw.circle(surf, dark,            (close_x + 1, close_y + 3), cs // 2)
    pygame.draw.circle(surf, col,             (close_x,     close_y),     cs // 2)
    pygame.draw.circle(surf, (255, 255, 255), (close_x,     close_y),     cs // 2, 2)
    sheen_s = pygame.Surface((cs, cs // 2), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen_s, (255, 255, 255, 50), (0, 0, cs, cs // 2))
    surf.blit(sheen_s, (close_x - cs // 2, close_y - cs // 2))
    x_s  = font_ft_body.render("X", True, WHITE)
    x_sh = font_ft_body.render("X", True, (0, 0, 0))
    x_sh.set_alpha(60)
    surf.blit(x_sh, (close_x - x_s.get_width() // 2 + 1, close_y - x_s.get_height() // 2 + 1))
    surf.blit(x_s,  (close_x - x_s.get_width() // 2,     close_y - x_s.get_height() // 2))
    draw_warning_overlay_on_top(surf)
    return None, close_rect_tp

# ══════════════════════════════════════════════════════════════════════════════
# ── Classroom drawing ─────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def draw_classroom(surf, dt):
    global classroom_timer, classroom_running
    surf.blit(bg_classroom, (0, 0))
    if classroom_running and not all(tasks_done):
        classroom_timer = max(0, classroom_timer - dt)
        if classroom_timer <= 0:
            classroom_running = False
    minutes   = int(classroom_timer) // 60
    seconds   = int(classroom_timer) % 60
    timer_str = f"{minutes}:{seconds:02d}"

    TIMER_X = 550; TIMER_Y = 28; TIMER_W = 235; TIMER_H = 65
    pygame.draw.rect(surf, (100, 60, 20), (TIMER_X+2, TIMER_Y+4, TIMER_W, TIMER_H), border_radius=13)
    pygame.draw.rect(surf, (139, 90, 43), (TIMER_X,   TIMER_Y,   TIMER_W, TIMER_H), border_radius=13)
    ic_cx, ic_cy, ic_r = TIMER_X + 40, TIMER_Y + TIMER_H // 2, 21
    pygame.gfxdraw.filled_circle(surf, ic_cx, ic_cy, ic_r,     (100, 185, 230))
    pygame.gfxdraw.aacircle(surf,     ic_cx, ic_cy, ic_r,     ( 60, 140, 200))
    pygame.gfxdraw.filled_circle(surf, ic_cx, ic_cy, ic_r - 5, (200, 235, 255))
    ang = math.radians(-90 + (1 - classroom_timer / CLASSROOM_TIME) * 360)
    pygame.draw.line(surf, (40, 80, 140), (ic_cx, ic_cy),
                     (ic_cx + int(8*math.cos(ang)), ic_cy + int(8*math.sin(ang))), 2)
    pygame.draw.line(surf, (40, 80, 140), (ic_cx, ic_cy),
                     (ic_cx + int(6*math.cos(ang-math.pi/2)), ic_cy + int(6*math.sin(ang-math.pi/2))), 2)
    col_timer = (255, 80, 60) if classroom_timer < 30 else WHITE
    t_surf = font_timer.render(timer_str, True, col_timer)
    t_sh   = font_timer.render(timer_str, True, (0, 0, 0))
    t_sh.set_alpha(90)
    tx = TIMER_X + TIMER_W // 2 + 14 - t_surf.get_width() // 2
    ty = TIMER_Y + TIMER_H // 2      - t_surf.get_height() // 2
    surf.blit(t_sh,   (tx+2, ty+2))
    surf.blit(t_surf, (tx,   ty))

    ICON_FRACS = [
        (0.675, 0.360), (0.805, 0.360),
        (0.670, 0.550), (0.805, 0.550),
        (0.740, 0.740),
    ]
    ICON_R = 34
    icons  = []
    for i, (fx, fy) in enumerate(ICON_FRACS):
        cx_i = int(SCREEN_W * fx)
        cy_i = int(SCREEN_H * fy)
        icons.append((cx_i, cy_i, ICON_R))
        done = tasks_done[i]
        if done and task_anim[i] < 1.0:
            task_anim[i] = min(1.0, task_anim[i] + 0.06)
        if done:
            glow_r = int(ICON_R + 6 * task_anim[i])
            glow   = pygame.Surface((glow_r*2+4, glow_r*2+4), pygame.SRCALPHA)
            pygame.gfxdraw.filled_circle(glow, glow_r+2, glow_r+2, glow_r, (*GOLD, int(160*task_anim[i])))
            pygame.gfxdraw.aacircle(glow,     glow_r+2, glow_r+2, glow_r, (*GOLD, int(200*task_anim[i])))
            surf.blit(glow, (cx_i - glow_r - 2, cy_i - glow_r - 2))
            if check_img:
                alpha_surf = check_img.copy()
                alpha_surf.set_alpha(int(255 * task_anim[i]))
                surf.blit(alpha_surf, (cx_i - CHECK_ICON_SIZE // 2,
                                       cy_i - CHECK_ICON_SIZE // 2))
            else:
                chk    = font_timer.render("V", True, WHITE)
                chk_sh = font_timer.render("V", True, (0, 0, 0))
                chk_sh.set_alpha(80)
                surf.blit(chk_sh, (cx_i - chk.get_width()//2 + 2, cy_i - chk.get_height()//2 + 2))
                surf.blit(chk,    (cx_i - chk.get_width()//2,     cy_i - chk.get_height()//2))
        else:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003 + i)) * 0.5 + 0.5
            ring  = pygame.Surface((ICON_R*2+8, ICON_R*2+8), pygame.SRCALPHA)
            pygame.gfxdraw.aacircle(ring, ICON_R+4, ICON_R+4, ICON_R+2,
                                    (255, 230, 100, int(70 * pulse)))
            surf.blit(ring, (cx_i - ICON_R - 4, cy_i - ICON_R - 4))

    mx_t, my_t = pygame.mouse.get_pos()
    for i, (cx_i, cy_i, ir) in enumerate(icons):
        if ((mx_t-cx_i)**2 + (my_t-cy_i)**2)**0.5 <= ir and not tasks_done[i]:
            tip    = font_small.render(f"Click: {CLASSROOM_TASKS[i]}", True, WHITE)
            tip_bg = pygame.Surface((tip.get_width()+16, tip.get_height()+8), pygame.SRCALPHA)
            tip_bg.fill((0, 0, 0, 160))
            surf.blit(tip_bg, (cx_i - tip.get_width()//2 - 8, cy_i + ir + 6))
            surf.blit(tip,    (cx_i - tip.get_width()//2,      cy_i + ir + 10))
            break

    draw_smooth_rect(surf, (30,30,40), (BACK_RECT.x, BACK_RECT.y, BACK_RECT.w, BACK_RECT.h), radius=8)
    outline = pygame.Surface((BACK_RECT.w, BACK_RECT.h), pygame.SRCALPHA)
    pygame.draw.rect(outline, (255,255,255,60), (0,0,BACK_RECT.w,BACK_RECT.h), 1, border_radius=8)
    surf.blit(outline, (BACK_RECT.x, BACK_RECT.y))
    back = font_small.render("Back to Map", True, WHITE)
    surf.blit(back, (BACK_RECT.x+12, BACK_RECT.y+10))

    _update_and_draw_teacher(surf, dt)

    if not classroom_running and classroom_timer <= 0 and not all(tasks_done) and not teacher_caught_player:
        _draw_result_banner(surf, win=False, reason="time")
    elif all(tasks_done):
        _draw_result_banner(surf, win=True, reason="")

    draw_mute_button(surf)
    return icons

# ══════════════════════════════════════════════════════════════════════════════
# ── Teacher AI ────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
_teacher_was_walking = False

def _update_and_draw_teacher(surf, dt):
    global teacher_state, teacher_x, teacher_direction
    global teacher_next_time, teacher_pause_timer, teacher_warn_timer
    global teacher_caught_player, classroom_running, teacher_suspicion
    global teacher_patrol_timer, active_task
    global ft_active, wt_active, ss_active, wm_active, cl_active
    global _teacher_was_walking

    tw = teacher_walk_img.get_width()

    teacher_is_nearby = teacher_state in ("walking", "patrolling")

    if teacher_is_nearby and not _teacher_was_walking:
        play_warning_sound()
        _teacher_was_walking = True
    elif not teacher_is_nearby and _teacher_was_walking:
        stop_warning_sound()
        _teacher_was_walking = False

    if teacher_state == "idle":
        if not classroom_running:
            return
        teacher_next_time -= dt
        if teacher_next_time <= 0:
            teacher_direction = random.choice([-1, 1])
            teacher_x         = float(-tw) if teacher_direction == 1 else float(SCREEN_W + tw)
            teacher_state     = "walking"
            teacher_suspicion = False
            _update_and_draw_teacher._sus      = 0.0
            _update_and_draw_teacher._patrolled = False

    elif teacher_state == "walking":
        teacher_x += teacher_direction * TEACHER_WALK_SPEED * dt
        centre   = SCREEN_W * 0.38
        dist_ctr = abs(teacher_x + tw // 2 - centre)

        if dist_ctr < 80 and not getattr(_update_and_draw_teacher, '_patrolled', False):
            teacher_state        = "patrolling"
            teacher_patrol_timer = random.uniform(TEACHER_PATROL_MIN, TEACHER_PATROL_MAX)

        player_is_busy = (active_task is not None) or ft_active or wt_active or ss_active or wm_active or cl_active
        if player_is_busy and classroom_running and not teacher_caught_player:
            sus = getattr(_update_and_draw_teacher, '_sus', 0.0)
            _update_and_draw_teacher._sus = min(1.0, sus + dt * 0.5)
        else:
            sus = getattr(_update_and_draw_teacher, '_sus', 0.0)
            _update_and_draw_teacher._sus = max(0.0, sus - dt * 2.5)

        if teacher_direction == 1 and teacher_x > SCREEN_W + 20:
            teacher_state         = "idle"
            teacher_caught_player = False
            _update_and_draw_teacher._sus      = 0.0
            _update_and_draw_teacher._patrolled = False
            teacher_next_time = random.uniform(TEACHER_INTERVAL_MIN, TEACHER_INTERVAL_MAX)
            if not all(tasks_done):
                classroom_running = True
        elif teacher_direction == -1 and teacher_x + tw < -20:
            teacher_state         = "idle"
            teacher_caught_player = False
            _update_and_draw_teacher._sus      = 0.0
            _update_and_draw_teacher._patrolled = False
            teacher_next_time = random.uniform(TEACHER_INTERVAL_MIN, TEACHER_INTERVAL_MAX)
            if not all(tasks_done):
                classroom_running = True

    elif teacher_state == "patrolling":
        teacher_patrol_timer -= dt

        player_is_busy = (active_task is not None) or ft_active or wt_active or ss_active or wm_active or cl_active
        if player_is_busy and classroom_running and not teacher_caught_player:
            sus = getattr(_update_and_draw_teacher, '_sus', 0.0)
            sus = min(1.0, sus + dt * 1.4)
            _update_and_draw_teacher._sus = sus
            if sus >= 1.0:
                teacher_state         = "caught"
                teacher_pause_timer   = TEACHER_PAUSE_TIME
                teacher_warn_timer    = TEACHER_WARN_TIME
                teacher_caught_player = True
                classroom_running     = False
                _update_and_draw_teacher._sus = 0.0
                stop_warning_sound()
                stop_task_music()
                play_sound(sfx_lose)
                ft_active   = False
                wt_active   = False
                ss_active   = False
                wm_active   = False
                cl_active   = False
                active_task = None
        else:
            sus = getattr(_update_and_draw_teacher, '_sus', 0.0)
            _update_and_draw_teacher._sus = max(0.0, sus - dt * 3.0)

        if teacher_patrol_timer <= 0 and teacher_state == "patrolling":
            teacher_state = "walking"
            _update_and_draw_teacher._patrolled = True

    elif teacher_state == "caught":
        teacher_pause_timer -= dt
        teacher_warn_timer  -= dt
        if teacher_pause_timer <= 0:
            teacher_state = "leaving"

    elif teacher_state == "leaving":
        teacher_x += teacher_direction * TEACHER_WALK_SPEED * dt
        if teacher_direction == 1 and teacher_x > SCREEN_W + 20:
            teacher_state     = "idle"
            _update_and_draw_teacher._patrolled = False
            teacher_next_time = random.uniform(TEACHER_INTERVAL_MIN, TEACHER_INTERVAL_MAX)
        elif teacher_direction == -1 and teacher_x + tw < -20:
            teacher_state     = "idle"
            _update_and_draw_teacher._patrolled = False
            teacher_next_time = random.uniform(TEACHER_INTERVAL_MIN, TEACHER_INTERVAL_MAX)

    if teacher_state not in ("walking", "patrolling", "caught", "leaving"):
        return

    img = teacher_caught_img if teacher_state == "caught" else teacher_walk_img
    if teacher_direction == -1:
        img = pygame.transform.flip(img, True, False)

    th = img.get_height()
    tw = img.get_width()
    ty = int(SCREEN_H * 0.55) - th
    tx = int(teacher_x)

    shadow_w, shadow_h = tw // 2, 18
    shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 70), (0, 0, shadow_w, shadow_h))
    surf.blit(shadow_surf, (tx + tw // 4, ty + th - shadow_h // 2))

    if teacher_state == "caught":
        pulse   = abs(math.sin(pygame.time.get_ticks() * 0.008)) * 0.5 + 0.5
        glow_sz = max(tw, th) + 60
        glow    = pygame.Surface((glow_sz, glow_sz), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 50, 20, int(90 * pulse)), (0, 0, glow_sz, glow_sz))
        surf.blit(glow, (tx + tw // 2 - glow_sz // 2, ty + th // 2 - glow_sz // 2))

    surf.blit(img, (tx, ty))

    sus_level = getattr(_update_and_draw_teacher, '_sus', 0.0)
    if sus_level > 0.05 and teacher_state in ("walking", "patrolling"):
        bar_w = 80; bar_h = 10
        bx    = tx + tw // 2 - bar_w // 2
        by    = ty - 28
        pygame.draw.rect(surf, (60, 20, 20), (bx-1, by-1, bar_w+2, bar_h+2), border_radius=5)
        fill_col = (255, int(200 * (1 - sus_level)), 0)
        pygame.draw.rect(surf, fill_col, (bx, by, int(bar_w * sus_level), bar_h), border_radius=4)
        thought = "?!" if sus_level < 0.6 else "!!"
        sus_lbl = font_small.render(f"{thought} Suspicious", True, (255, 220, 60))
        surf.blit(sus_lbl, (bx + bar_w // 2 - sus_lbl.get_width() // 2, by - 16))

    if teacher_state == "caught":
        excl = font_title.render("!", True, (255, 60, 30))
        surf.blit(excl, (tx + tw // 2 - excl.get_width() // 2, ty - excl.get_height() - 8))

    if teacher_state in ("walking", "patrolling") and not (ft_active or wt_active or ss_active or wm_active or cl_active or active_task is not None):
        pulse      = abs(math.sin(pygame.time.get_ticks() * 0.006))
        warn_alpha = int(180 + 75 * pulse)
        banner = pygame.Surface((SCREEN_W, 30), pygame.SRCALPHA)
        banner.fill((200, 30, 20, int(warn_alpha * 0.55)))
        surf.blit(banner, (0, SCREEN_H - 30))
        warn_msg = font_small.render(
            "WARNING  TEACHER NEARBY — close your task and stay still!",
            True, (255, 230, 80)
        )
        surf.blit(warn_msg, (SCREEN_W // 2 - warn_msg.get_width() // 2, SCREEN_H - 22))
        vignette = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        edge_alpha = int(80 * pulse)
        pygame.draw.rect(vignette, (220, 30, 20, edge_alpha),
                         (0, 0, SCREEN_W, SCREEN_H), 22)
        surf.blit(vignette, (0, 0))

# ══════════════════════════════════════════════════════════════════════════════
# ── Caught overlay ────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
caught_try_again_rect = pygame.Rect(0, 0, 0, 0)
caught_back_rect      = pygame.Rect(0, 0, 0, 0)

def _draw_caught_overlay(surf):
    global caught_try_again_rect, caught_back_rect

    tint = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    tint.fill((80, 0, 0, 70))
    surf.blit(tint, (0, 0))

    pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.6 + 0.4
    border = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    pygame.draw.rect(border, (220, 30, 20, int(160 * pulse)),
                     (0, 0, SCREEN_W, SCREEN_H), 20)
    surf.blit(border, (0, 0))

    CAUGHT_DISPLAY_H = 300
    raw_w = teacher_caught_img.get_width()
    raw_h = teacher_caught_img.get_height()
    caught_scale = CAUGHT_DISPLAY_H / raw_h
    caught_w = int(raw_w * caught_scale)
    caught_h = CAUGHT_DISPLAY_H

    teacher_display_big = pygame.transform.smoothscale(teacher_caught_img, (caught_w, caught_h))
    if teacher_direction == 1:
        teacher_display_big = pygame.transform.flip(teacher_display_big, True, False)

    th   = caught_h
    tw_d = caught_w

    PW2, PH2 = 460, 270
    PANEL_OFFSET_X = -90
    px2 = SCREEN_W // 2 - PW2 // 2 + PANEL_OFFSET_X
    py2 = SCREEN_H // 2 - PH2 // 2

    teacher_x_draw = px2 + PW2 + 10
    teacher_y_draw = py2 + PH2 - th
    teacher_x_draw = min(teacher_x_draw, SCREEN_W - tw_d - 4)
    teacher_y_draw = max(teacher_y_draw, 0)

    glow_sz = max(tw_d, th) + 70
    glow = pygame.Surface((glow_sz, glow_sz), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255, 50, 20, int(90 * pulse)), (0, 0, glow_sz, glow_sz))
    surf.blit(glow, (teacher_x_draw + tw_d // 2 - glow_sz // 2,
                     teacher_y_draw + th // 2 - glow_sz // 2))

    shadow_surf = pygame.Surface((tw_d, 22), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, tw_d, 22))
    surf.blit(shadow_surf, (teacher_x_draw, teacher_y_draw + th - 11))
    surf.blit(teacher_display_big, (teacher_x_draw, teacher_y_draw))

    excl = font_timer.render("!", True, (255, 60, 30))
    excl_sh = font_timer.render("!", True, (0, 0, 0))
    excl_sh.set_alpha(70)
    ex = teacher_x_draw + tw_d // 2 - excl.get_width() // 2
    ey = max(4, teacher_y_draw - excl.get_height() - 4)
    surf.blit(excl_sh, (ex + 2, ey + 2))
    surf.blit(excl,    (ex,     ey))

    panel = pygame.Surface((PW2, PH2), pygame.SRCALPHA)
    pygame.draw.rect(panel, (80, 10, 10, 220), (0, 0, PW2, PH2), border_radius=20)
    pygame.draw.rect(panel, (200, 50, 30, 255), (0, 0, PW2, PH2), 3, border_radius=20)

    title_s = font_title.render("You were caught!", True, (255, 80, 60))
    sub_s   = font_large.render("The teacher saw you with your pet.", True, (220, 180, 160))
    hint_s  = font_small.render("Close the task frame when the teacher walks by!", True, (180, 150, 130))
    panel.blit(title_s, (PW2 // 2 - title_s.get_width() // 2, 22))
    panel.blit(sub_s,   (PW2 // 2 - sub_s.get_width()   // 2, 68))
    panel.blit(hint_s,  (PW2 // 2 - hint_s.get_width()  // 2, 104))

    mx_l = pygame.mouse.get_pos()[0] - px2
    my_l = pygame.mouse.get_pos()[1] - py2

    ta_w, ta_h = 175, 46
    ta_x = PW2 // 2 - ta_w - 10
    ta_y = PH2 - 68
    ta_hov = pygame.Rect(ta_x, ta_y, ta_w, ta_h).collidepoint(mx_l, my_l)
    ta_col = (80, 175, 55) if ta_hov else (55, 140, 35)
    pygame.draw.rect(panel, (30, 90, 15),  (ta_x+2, ta_y+4, ta_w, ta_h), border_radius=ta_h // 2)
    pygame.draw.rect(panel, ta_col,         (ta_x,   ta_y,   ta_w, ta_h), border_radius=ta_h // 2)
    ta_lbl = font_play.render("Try Again", True, WHITE)
    panel.blit(ta_lbl, (ta_x + ta_w // 2 - ta_lbl.get_width() // 2,
                        ta_y + ta_h // 2 - ta_lbl.get_height() // 2))

    bk_w, bk_h = 175, 46
    bk_x = PW2 // 2 + 10
    bk_y = PH2 - 68
    bk_hov = pygame.Rect(bk_x, bk_y, bk_w, bk_h).collidepoint(mx_l, my_l)
    bk_col = (185, 55, 40) if bk_hov else (145, 35, 25)
    pygame.draw.rect(panel, (90, 20, 10),  (bk_x+2, bk_y+4, bk_w, bk_h), border_radius=bk_h // 2)
    pygame.draw.rect(panel, bk_col,         (bk_x,   bk_y,   bk_w, bk_h), border_radius=bk_h // 2)
    bk_lbl = font_play.render("Back to Map", True, WHITE)
    panel.blit(bk_lbl, (bk_x + bk_w // 2 - bk_lbl.get_width() // 2,
                        bk_y + bk_h // 2 - bk_lbl.get_height() // 2))

    surf.blit(panel, (px2, py2))

    caught_try_again_rect = pygame.Rect(px2 + ta_x, py2 + ta_y, ta_w, ta_h)
    caught_back_rect      = pygame.Rect(px2 + bk_x, py2 + bk_y, bk_w, bk_h)

def _draw_result_banner(surf, win, reason=""):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surf.blit(overlay, (0, 0))
    if win:
        msg = font_title.render("You Did It! All tasks done!", True, GOLD_LIGHT)
        sub = font_large.render("Your pet is happy  :)", True, WHITE)
    else:
        msg = font_title.render("Time's up!", True, (255, 100, 80))
        sub = font_large.render("You ran out of time...", True, WHITE)
    surf.blit(msg, (SCREEN_W//2 - msg.get_width()//2, SCREEN_H//2 - 40))
    surf.blit(sub, (SCREEN_W//2 - sub.get_width()//2, SCREEN_H//2 + 10))
    hint = font_small.render("Press ESC to return to map", True, (200, 200, 200))
    surf.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H//2 + 45))

# ══════════════════════════════════════════════════════════════════════════════
# ── Misc helpers ──────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
click_flash  = {}
FLASH_FRAMES = 14

def fade_transition(from_bg, to_bg, ms=500):
    steps   = max(1, ms // 16)
    overlay = pygame.Surface((SCREEN_W, SCREEN_H))
    for i in range(steps + 1):
        screen.blit(from_bg, (0, 0))
        overlay.blit(to_bg, (0, 0))
        overlay.set_alpha(int(255 * i / steps))
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        pygame.event.pump()

def get_popup_play_rect():
    local = _play_rect_local()
    return pygame.Rect(PX + local.x, PY + local.y, local.w, local.h)

def get_popup_close_rect():
    local = _close_rect_local()
    return pygame.Rect(PX + local.x, PY + local.y, local.w, local.h)

BACK_RECT = pygame.Rect(10, 10, 185, 36)
MUTE_RECT   = pygame.Rect(SCREEN_W - 44, 10, 34, 34)
show_sound_popup      = False
sound_popup_anim      = 0.0
SOUND_POPUP_SPEED     = 0.12
sound_dragging_slider = None
_sound_popup_rects    = {}

# ══════════════════════════════════════════════════════════════════════════════
# ── State machine ─────────────────────────────────────────────────════════════
# ══════════════════════════════════════════════════════════════════════════════
state    = "landing"
hov_land = None
hov_map  = None

show_popup  = False
popup_anim  = 0.0
POPUP_SPEED = 0.12

show_howto = False
howto_anim = 0.0

classroom_icon_positions = []
_task_popup_action_rect  = None
_task_popup_close_rect   = None
active_task              = None
task_popup_anim          = 0.0
TASK_POPUP_SPEED         = 0.14
task_clicks              = [0] * len(CLASSROOM_TASKS)
TASK_CLICKS_NEEDED       = [3, 2, 4, 3, 2]
TASK_DESCS = [
    "Feed your pet some kibble!",
    "Fill the water bowl up.",
    "Shh! Calm your noisy pet.",
    "Toss a toy to distract them.",
    "Clean up the mess quietly.",
]
TASK_ACTION_LABELS = ["Feed", "Fill", "Shhhh", "Toss", "Clean"]
dt = 0.0

# ══════════════════════════════════════════════════════════════════════════════
# ── Main loop ─────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
running = True
while running:
    mx, my = pygame.mouse.get_pos()
    dt     = clock.get_time() / 1000.0

    if show_sound_popup:
        sound_popup_anim = min(1.0, sound_popup_anim + SOUND_POPUP_SPEED)
    else:
        sound_popup_anim = max(0.0, sound_popup_anim - SOUND_POPUP_SPEED * 2.5)
    if show_popup and popup_anim < 1.0:
        popup_anim = min(1.0, popup_anim + POPUP_SPEED)
    if show_howto and howto_anim < 1.0:
        howto_anim = min(1.0, howto_anim + POPUP_SPEED)
    if show_locked and locked_anim < 1.0:
        locked_anim = min(1.0, locked_anim + LOCKED_SPEED)
    if show_settings and settings_anim < 1.0:
        settings_anim = min(1.0, settings_anim + SETTINGS_SPEED)

    for rid in list(click_flash.keys()):
        click_flash[rid] -= 1
        if click_flash[rid] <= 0:
            del click_flash[rid]

    play_rect  = get_popup_play_rect()
    close_rect = get_popup_close_rect()

    events_this_frame = pygame.event.get()

    # ── Route events to the active minigame ──────────────────────────────────
    if ft_active:
        ft_done, ft_cancelled = ft_update(events_this_frame, dt)
        if ft_done:
            tasks_done[0] = True
        for event in events_this_frame:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                sound_dragging_slider = None

    elif wt_active:
        wt_done, wt_cancelled = wt_update(events_this_frame, dt)
        if wt_done:
            tasks_done[1] = True
        for event in events_this_frame:
            if event.type == pygame.QUIT:
                running = False

    elif ss_active:
        ss_done, ss_cancelled = ss_update(events_this_frame, dt)
        if ss_done:
            tasks_done[2] = True
        for event in events_this_frame:
            if event.type == pygame.QUIT:
                running = False

    elif wm_active:
        wm_done, wm_cancelled = wm_update(events_this_frame, dt)
        if wm_done:
            tasks_done[3] = True
        for event in events_this_frame:
            if event.type == pygame.QUIT:
                running = False

    elif cl_active:
        cl_done, cl_cancelled = cl_update(events_this_frame, dt)
        if cl_done:
            tasks_done[4] = True
        for event in events_this_frame:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                sound_dragging_slider = None

    else:
        for event in events_this_frame:
            if event.type == pygame.QUIT:
                running = False

            # ── Slider mouse motion ───────────────────────────────────────────
            if event.type == pygame.MOUSEMOTION:
                if show_settings and settings_dragging_slider:
                    scale_s   = 0.6 + 0.4 * settings_anim
                    bar_x_s   = 60
                    bar_w_s   = SPW_BASE - 160
                    spx_s     = SCREEN_W // 2 - int(SPW_BASE * scale_s) // 2
                    for si, key in enumerate(["music", "sfx", "ambience"]):
                        if settings_dragging_slider == key:
                            track_x = spx_s + int(bar_x_s * scale_s)
                            track_w = int(bar_w_s * scale_s)
                            new_val = max(0.0, min(1.0, (mx - track_x) / max(1, track_w)))
                            if key == "music":
                                vol_music = new_val
                                pygame.mixer.music.set_volume(new_val)
                            elif key == "sfx":
                                vol_sfx = new_val
                                CLICK_CHANNEL.set_volume(new_val)
                            elif key == "ambience":
                                vol_ambience = new_val
                                AMBIENCE_CHANNEL.set_volume(new_val)
                            break

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                settings_dragging_slider = None
                sound_dragging_slider    = None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if show_settings:
                    show_settings = False
                    settings_anim = 0.0
                elif show_locked:
                    show_locked = False
                    locked_anim = 0.0
                elif show_popup:
                    show_popup = False
                    popup_anim = 0.0
                elif state == "classroom":
                    stop_classroom_ambience()
                    stop_warning_sound()
                    stop_task_music()
                    fade_transition(bg_classroom, bg_map)
                    state = "map"
                    pygame.mixer.music.play(loops=-1)
                elif state == "map":
                    fade_transition(bg_map, bg_landing)
                    state = "landing"
                else:
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if MUTE_RECT.collidepoint(mx, my):
                    toggle_sound_popup()

                elif show_sound_popup:
                    _slider_keys = [k for k in ("music", "sfx", "ambience") if k in _sound_popup_rects]
                    _hit_slider = False
                    for _key in _slider_keys:
                        _r = _sound_popup_rects.get(_key)
                        if _r and _r.collidepoint(mx, my):
                            sound_dragging_slider = _key
                            _hit_slider = True
                            break
                    if not _hit_slider:
                        _mr = _sound_popup_rects.get("mute")
                        if _mr and _mr.collidepoint(mx, my):
                            toggle_mute()
                        elif not _sound_popup_rects.get("panel", pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                            show_sound_popup = False
                            sound_popup_anim = 0.0

                elif show_settings:
                    if settings_close_rect.collidepoint(mx, my):
                        play_sound(sfx_click)
                        show_settings = False
                        settings_anim = 0.0
                    else:
                        # Check if clicking a slider track to start dragging
                        scale_s   = 0.6 + 0.4 * settings_anim
                        spw_s_now = int(SPW_BASE * scale_s)
                        sph_s_now = int(SPH_BASE * scale_s)
                        spx_s     = SCREEN_W // 2 - spw_s_now // 2
                        spy_s     = SCREEN_H // 2 - sph_s_now // 2
                        bar_x_s   = 60
                        bar_w_s   = SPW_BASE - 160
                        bar_h_s   = 18
                        start_y_s = 90
                        row_gap_s = 72
                        hit_slider = False
                        for si, key in enumerate(["music", "sfx", "ambience"]):
                            by_s  = start_y_s + si * row_gap_s
                            track = pygame.Rect(
                                spx_s + int(bar_x_s * scale_s),
                                spy_s + int(by_s    * scale_s),
                                int(bar_w_s * scale_s),
                                int(bar_h_s * scale_s) + 10,
                            )
                            if track.collidepoint(mx, my):
                                settings_dragging_slider = key
                                hit_slider = True
                                # Immediately update value on click
                                track_x = spx_s + int(bar_x_s * scale_s)
                                track_w = int(bar_w_s * scale_s)
                                new_val = max(0.0, min(1.0, (mx - track_x) / max(1, track_w)))
                                if key == "music":
                                    vol_music = new_val
                                    pygame.mixer.music.set_volume(new_val)
                                elif key == "sfx":
                                    vol_sfx = new_val
                                    CLICK_CHANNEL.set_volume(new_val)
                                elif key == "ambience":
                                    vol_ambience = new_val
                                    AMBIENCE_CHANNEL.set_volume(new_val)
                                break
                        if not hit_slider:
                            # Click outside panel closes it
                            panel_rect_s = pygame.Rect(spx_s, spy_s, spw_s_now, sph_s_now)
                            if not panel_rect_s.collidepoint(mx, my):
                                show_settings = False
                                settings_anim = 0.0

                elif show_locked:
                    if locked_okay_rect.collidepoint(mx, my):
                        play_sound(sfx_click)
                        show_locked = False
                        locked_anim = 0.0
                    elif not pygame.Rect(LPX, LPY, LPW, LPH).collidepoint(mx, my):
                        show_locked = False
                        locked_anim = 0.0

                elif show_howto:
                    if howto_close_rect.collidepoint(mx, my):
                        play_sound(sfx_click)
                        show_howto = False
                        howto_anim = 0.0

                elif show_popup:
                    if close_rect.collidepoint(mx, my):
                        play_sound(sfx_click)
                        show_popup = False
                        popup_anim = 0.0
                    elif play_rect.collidepoint(mx, my):
                        play_sound(sfx_click)
                        show_popup        = False
                        popup_anim        = 0.0
                        fade_transition(bg_map, bg_classroom)
                        pygame.mixer.music.stop()
                        start_classroom_ambience()
                        start_task_music()
                        state             = "classroom"
                        classroom_timer   = CLASSROOM_TIME
                        classroom_running = True
                        tasks_done        = [False] * len(CLASSROOM_TASKS)
                        task_anim         = [0.0]  * len(CLASSROOM_TASKS)
                        teacher_state         = "idle"
                        teacher_next_time     = 8.0
                        teacher_caught_player = False
                        active_task           = None
                        task_popup_anim       = 0.0
                        task_clicks           = [0] * len(CLASSROOM_TASKS)
                        _teacher_was_walking  = False
                    elif not pygame.Rect(PX, PY, PW, PH).collidepoint(mx, my):
                        show_popup = False
                        popup_anim = 0.0

                elif state == "landing":
                    for btn in landing_buttons:
                        bx, by, bw, bh = btn["rect"]
                        if bx <= mx <= bx+bw and by <= my <= by+bh:
                            play_sound(sfx_click)
                            if btn["id"] == "start":
                                fade_transition(bg_landing, bg_map)
                                state = "map"
                            elif btn["id"] == "settings":
                                show_settings = True
                                settings_anim = 0.0
                            elif btn["id"] == "howto":
                                show_howto = True
                                howto_anim = 0.0

                elif state == "classroom":
                    if MUTE_RECT.collidepoint(mx, my):
                        toggle_sound_popup()
                    elif show_sound_popup:
                        _slider_keys = [k for k in ("music", "sfx", "ambience") if k in _sound_popup_rects]
                        _hit_slider = False
                        for _key in _slider_keys:
                            _r = _sound_popup_rects.get(_key)
                            if _r and _r.collidepoint(mx, my):
                                sound_dragging_slider = _key
                                _hit_slider = True
                                break
                        if not _hit_slider:
                            _mr = _sound_popup_rects.get("mute")
                            if _mr and _mr.collidepoint(mx, my):
                                toggle_mute()
                            elif not _sound_popup_rects.get("panel", pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                                show_sound_popup = False
                                sound_popup_anim = 0.0
                    elif teacher_caught_player and not classroom_running:
                        if caught_try_again_rect.width > 0 and caught_try_again_rect.collidepoint(mx, my):
                            play_sound(sfx_click)
                            teacher_caught_player = False
                            classroom_running     = True
                            teacher_state         = "idle"
                            teacher_next_time     = 5.0
                            tasks_done            = [False] * len(CLASSROOM_TASKS)
                            task_anim             = [0.0]  * len(CLASSROOM_TASKS)
                            task_clicks           = [0] * len(CLASSROOM_TASKS)
                            active_task           = None
                            classroom_timer       = CLASSROOM_TIME
                            _update_and_draw_teacher._sus      = 0.0
                            _update_and_draw_teacher._patrolled = False
                            _teacher_was_walking  = False
                            start_task_music()
                        elif caught_back_rect.width > 0 and caught_back_rect.collidepoint(mx, my):
                            play_sound(sfx_click)
                            stop_classroom_ambience()
                            stop_warning_sound()
                            stop_task_music()
                            fade_transition(bg_classroom, bg_map)
                            state = "map"
                            pygame.mixer.music.play(loops=-1)
                            teacher_caught_player = False
                            classroom_running     = False
                    elif BACK_RECT.collidepoint(mx, my):
                        play_sound(sfx_click)
                        stop_classroom_ambience()
                        stop_warning_sound()
                        stop_task_music()
                        fade_transition(bg_classroom, bg_map)
                        state = "map"
                        pygame.mixer.music.play(loops=-1)
                    elif active_task is not None:
                        if _task_popup_action_rect and _task_popup_action_rect.collidepoint(mx, my):
                            play_sound(sfx_click)
                            idx = active_task
                            if task_clicks[idx] < TASK_CLICKS_NEEDED[idx]:
                                task_clicks[idx] += 1
                            if task_clicks[idx] >= TASK_CLICKS_NEEDED[idx]:
                                play_sound(sfx_task_complete)
                                tasks_done[idx] = True
                                active_task     = None
                                task_popup_anim = 0.0
                        elif _task_popup_close_rect and _task_popup_close_rect.collidepoint(mx, my):
                            play_sound(sfx_click)
                            active_task     = None
                            task_popup_anim = 0.0
                    else:
                        if teacher_state not in ("walking", "patrolling", "caught", "leaving"):
                            for i, (cx_i, cy_i, ir) in enumerate(classroom_icon_positions):
                                dist = ((mx - cx_i)**2 + (my - cy_i)**2) ** 0.5
                                if dist <= ir and not tasks_done[i]:
                                    play_sound(sfx_click)
                                    if i == 0:
                                        ft_open()
                                    elif i == 1:
                                        wt_open()
                                    elif i == 2:
                                        ss_open()
                                    elif i == 3:
                                        wm_open()
                                    elif i == 4:
                                        cl_open()
                                    else:
                                        active_task     = i
                                        task_popup_anim = 0.0
                                    break

                elif state == "map":
                    if MUTE_RECT.collidepoint(mx, my):
                        toggle_sound_popup()
                    elif CARD_CLASSROOM_RECT.collidepoint(mx, my):
                        play_sound(sfx_click)
                        show_popup = True
                        popup_anim = 0.0
                    elif CARD_LIBRARY_RECT.collidepoint(mx, my):
                        play_sound(sfx_click)
                        show_locked = True
                        locked_anim = 0.0
                    elif BACK_EXIT_RECT.collidepoint(mx, my):
                        play_sound(sfx_click)
                        fade_transition(bg_map, bg_landing)
                        state = "landing"

    # ── Hover / cursor detection ──────────────────────────────────────────────
    if ft_active:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        bw2 = ft_img_bag.get_width()
        bh2 = ft_img_bag.get_height()
        bx2 = ft_bag_pos[0] - bw2 // 2
        by2 = ft_bag_pos[1] - bh2 // 2
        if pygame.Rect(bx2, by2, bw2, bh2).collidepoint(mx, my) or ft_close_rect.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    elif wt_active:
        if wt_btn_rect.collidepoint(mx, my) or wt_close_rect.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif ss_active:
        if ss_close_rect.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif wm_active:
        if wm_close_rect.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif cl_active:
        if cl_close_rect.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif cl_panel_rect.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif show_settings:
        if settings_close_rect.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif show_locked:
        if locked_okay_rect.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif show_howto:
        if howto_close_rect.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif show_popup:
        popup_play_hovered  = play_rect.collidepoint(mx, my)
        popup_close_hovered = close_rect.collidepoint(mx, my)
        if popup_play_hovered or popup_close_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif state == "classroom":
        cursor_set = False
        if teacher_caught_player and not classroom_running:
            if caught_try_again_rect.collidepoint(mx, my) or caught_back_rect.collidepoint(mx, my):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                cursor_set = True
        if not cursor_set and BACK_RECT.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            cursor_set = True
        if not cursor_set and _task_popup_close_rect and _task_popup_close_rect.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            cursor_set = True
        if not cursor_set:
            for cx_i, cy_i, ir in classroom_icon_positions:
                if ((mx-cx_i)**2 + (my-cy_i)**2)**0.5 <= ir:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    cursor_set = True
                    break
        if not cursor_set:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif state == "landing":
        hov_land = None
        for btn in landing_buttons:
            bx, by, bw, bh = btn["rect"]
            if bx <= mx <= bx+bw and by <= my <= by+bh:
                hov_land = btn["id"]
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                break
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    elif state == "map":
        hov_map    = None
        cursor_set = False
        if MUTE_RECT.collidepoint(mx, my):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            cursor_set = True
        for rect, rid in [
            (CARD_CLASSROOM_RECT, "classroom"),
            (CARD_LIBRARY_RECT,   "library"),
            (BACK_EXIT_RECT,      "back"),
        ]:
            if rect.collidepoint(mx, my):
                hov_map    = rid
                cursor_set = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                break
        if not cursor_set:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # ── Draw ──────────────────────────────────────────────────────────────────
    if state == "landing":
        screen.blit(bg_landing, (0, 0))
        for btn in landing_buttons:
            draw_modern_button(
                screen, btn["rect"],
                btn["col"], btn["dark"], btn["hover"],
                btn["label"], btn["icon"],
                hov_land == btn["id"],
            )

    elif state == "map":
        draw_mode_select(screen, hov_map)

    elif state == "classroom":
        classroom_icon_positions = draw_classroom(screen, dt)

        if ft_active:
            ft_draw(screen)
        elif wt_active:
            wt_draw(screen)
        elif ss_active:
            ss_draw(screen)
        elif wm_active:
            wm_draw(screen)
        elif cl_active:
            cl_draw(screen)
        elif active_task is not None:
            task_popup_anim = min(1.0, task_popup_anim + TASK_POPUP_SPEED)
            _task_popup_action_rect, _task_popup_close_rect = draw_task_popup(
                screen, active_task, task_popup_anim)
        else:
            task_popup_anim         = 0.0
            _task_popup_action_rect = None
            _task_popup_close_rect  = None

        if teacher_caught_player:
            _draw_caught_overlay(screen)

    if show_popup:
        draw_popup(screen, popup_play_hovered, popup_close_hovered, popup_anim)

    if show_howto:
        draw_howto_popup(screen, howto_anim)

    if show_settings:
        draw_settings_popup(screen, settings_anim)

    if show_locked:
        draw_locked_popup(screen, locked_anim)

    if show_sound_popup or sound_popup_anim > 0.01:
        _rects = draw_sound_popup(screen, sound_popup_anim)
        if _rects:
            _sound_popup_rects.clear()
            _sound_popup_rects.update(_rects)
    else:
        _sound_popup_rects.clear()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()