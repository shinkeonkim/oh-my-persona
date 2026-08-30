from rest_framework import serializers

from common.choices.birth_time import BirthTime


class BirthTimeSerializer(serializers.Serializer):
    """
    Serializer for birth time choices.
    Returns all available birth time options with their display names.
    """

    value = serializers.CharField()
    label = serializers.CharField()

    @classmethod
    def get_choices_data(cls):
        """
        Get all birth time choices as a list of dictionaries.
        """
        return [{"value": choice[0], "label": choice[1]} for choice in BirthTime.choices]
