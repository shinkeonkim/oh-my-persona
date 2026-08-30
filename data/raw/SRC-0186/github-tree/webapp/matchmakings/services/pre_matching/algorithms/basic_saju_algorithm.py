from saju.services import SajuCompatibilityScoreService

from .base_algorithm import BaseAlgorithm


class BasicSajuAlgorithm(BaseAlgorithm):
    def calculate_score(self):
        male_user = self.prematching.male_user
        female_user = self.prematching.female_user

        male_user_profile = male_user.profile
        female_user_profile = female_user.profile

        saju_compatibility_score_service = SajuCompatibilityScoreService(male_user_profile, female_user_profile)
        self.score = saju_compatibility_score_service.compatibility_score
