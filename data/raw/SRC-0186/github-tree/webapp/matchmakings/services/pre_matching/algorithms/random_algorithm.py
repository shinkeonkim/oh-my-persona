import random

from .base_algorithm import BaseAlgorithm


class RandomAlgorithm(BaseAlgorithm):
    def calculate_score(self):
        self.score = random.randint(0, 100)
