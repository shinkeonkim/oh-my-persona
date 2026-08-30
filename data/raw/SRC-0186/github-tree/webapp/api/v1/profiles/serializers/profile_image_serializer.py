from rest_framework import serializers

from api.v1.file_managers.serializers import ImageSerializer
from file_managers.models import Image, ImageType
from profiles.models import ProfileImage


class ProfileImageSerializer(serializers.ModelSerializer):
    image = ImageSerializer(read_only=True)
    file = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = ProfileImage
        fields = (
            "id",
            "image",
            "file",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        """Create ProfileImage with uploaded file"""
        file = validated_data.pop("file")
        image = Image.objects.create(file=file, owner=self.context["request"].user, image_type=ImageType.PROFILE)

        validated_data["image"] = image
        return super().create(validated_data)
