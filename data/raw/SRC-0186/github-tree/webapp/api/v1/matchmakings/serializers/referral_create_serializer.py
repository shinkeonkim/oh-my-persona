from rest_framework import serializers

from common.choices import AlgorithmCategory


class ReferralCreateSerializer(serializers.Serializer):
    """새로운 추천 생성 시리얼라이저"""

    algorithm_type = serializers.ChoiceField(choices=AlgorithmCategory.get_choices(), help_text="추천 알고리즘 종류")
