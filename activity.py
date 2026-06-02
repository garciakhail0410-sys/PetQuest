from abc import ABC, abstractmethod

# ── PART 1: Abstract Base Class ──────────────────────────────────────────────
class PetTask(ABC):
    def __init__(self, name, difficulty):
        self.name = name
        self.difficulty = difficulty

    @abstractmethod
    def perform_action(self):
        pass

    @abstractmethod
    def special_skill(self):
        pass

    def __str__(self):
        return f"Task: {self.name} | Difficulty: {self.difficulty}"


# ── PART 2: Subclasses ────────────────────────────────────────────────────────
class FeedTask(PetTask):
    def __init__(self):
        super().__init__("Feed Your Pet", difficulty=3)

    def perform_action(self):
        print(f"{self.name} attacks using DRAG & DROP!")

    def special_skill(self):
        print(f"{self.name} uses KIBBLE SHOWER! (multiple drops at once)")


class WaterTask(PetTask):
    def __init__(self):
        super().__init__("Fill the Water Bowl", difficulty=2)

    def perform_action(self):
        print(f"{self.name} attacks using PUMP CLICK!")

    def special_skill(self):
        print(f"{self.name} uses RAPID PUMP! (water drains faster — stay alert!)")


class CalmTask(PetTask):
    def __init__(self):
        super().__init__("Calm Your Pet", difficulty=4)

    def perform_action(self):
        print(f"{self.name} attacks using SIMON SAYS PATTERN!")

    def special_skill(self):
        print(f"{self.name} uses NOISE SUPPRESSOR! (reduces noise bar instantly)")


class DistractTask(PetTask):
    def __init__(self):
        super().__init__("Distract with Toys", difficulty=3)

    def perform_action(self):
        print(f"{self.name} attacks using WHACK-A-MOLE STRIKE!")

    def special_skill(self):
        print(f"{self.name} uses TOY BLITZ! (all holes activate at once)")


class CleanTask(PetTask):
    def __init__(self):
        super().__init__("Clean Up the Mess", difficulty=2)

    def perform_action(self):
        print(f"{self.name} attacks using BROOM SWEEP!")

    def special_skill(self):
        print(f"{self.name} uses SPARKLE BURST! (clears all nearby dirt piles)")


# ── PART 3: Demonstrate Output ────────────────────────────────────────────────
tasks = [FeedTask(), WaterTask(), CalmTask(), DistractTask(), CleanTask()]

for task in tasks:
    print(task)
    task.perform_action()
    task.special_skill()
    print()