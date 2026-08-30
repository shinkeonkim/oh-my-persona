from rest_framework import serializers

from users.models import Child


class ChildSerializer(serializers.ModelSerializer):
    """
    Serializer for Child model.
    """

    class Meta:
        model = Child
        fields = [
            "id",
            "name",
            "birth_year",
            "gender",
        ]
