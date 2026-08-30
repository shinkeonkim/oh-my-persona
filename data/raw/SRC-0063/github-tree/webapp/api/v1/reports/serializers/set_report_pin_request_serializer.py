from rest_framework import serializers


class SetReportPinRequestSerializer(serializers.Serializer):
    pin = serializers.CharField(
        required=True,
        min_length=4,
        max_length=6,
        write_only=True,
        help_text="PIN은 4-6자리 숫자여야 합니다.",
        style={"input_type": "password"},
    )

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN은 숫자로만 구성되어야 합니다.")
        return value
