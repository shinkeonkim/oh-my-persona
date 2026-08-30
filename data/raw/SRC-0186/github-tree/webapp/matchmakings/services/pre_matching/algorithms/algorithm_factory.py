from importlib import import_module

from django.conf import settings

from matchmakings.models.pre_matching import PreMatching


class AlgorithmFactory:
    """
    알고리즘을 문자열로 선택할 수 있는 팩토리 클래스
    """

    @classmethod
    def create_algorithm(cls, algorithm_name: str, prematching: PreMatching):
        """
        알고리즘 이름을 받아서 해당 알고리즘의 인스턴스를 생성합니다.

        Args:
            algorithm_name (str): 알고리즘 이름
            prematching (PreMatching): PreMatching 인스턴스

        Returns:
            BaseAlgorithm: 알고리즘 인스턴스

        Raises:
            ValueError: 지원하지 않는 알고리즘 이름인 경우
        """
        algorithm_names = getattr(settings, "MATCHING_ALGORITHM_NAMES", [])
        if algorithm_name not in algorithm_names:
            available_algorithms = ", ".join(algorithm_names)
            raise ValueError(f"Unknown algorithm: {algorithm_name}. Available algorithms: {available_algorithms}")

        algorithm_class = import_module("matchmakings.services.pre_matching.algorithms")
        algorithm_class = algorithm_class.__getattribute__(algorithm_name)
        return algorithm_class(prematching)

    @classmethod
    def get_available_algorithms(cls):
        """
        사용 가능한 알고리즘 목록을 반환합니다.

        Returns:
            list: 사용 가능한 알고리즘 이름 목록
        """
        return getattr(settings, "MATCHING_ALGORITHM_NAMES", [])
