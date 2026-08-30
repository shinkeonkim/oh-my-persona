from matchmakings.models.pre_matching import PreMatching


class BaseAlgorithm:
    def __init__(self, prematching: PreMatching):
        self.prematching = prematching
        self.score = 0

    def calculate_score(self):
        pass

    def run(self):
        self.calculate_score()
        return self.score
