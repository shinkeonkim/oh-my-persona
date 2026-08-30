from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError


class BaseModelSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        try:
            return self.Meta.model.objects.create(**validated_data)
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict or e.messages)
