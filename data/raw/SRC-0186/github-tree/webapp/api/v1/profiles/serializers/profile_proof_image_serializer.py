from rest_framework import serializers

from api.v1.file_managers.serializers.image_serializer import ImageSerializer
from file_managers.models import Image, ImageType
from profiles.models import Profile


class ProfileProofImageSerializer(serializers.ModelSerializer):
    """
    Serializer for profile proof image.
    """

    image = ImageSerializer(source="proof_image", read_only=True)
    file = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = Profile
        fields = (
            "image",
            "file",
        )
        read_only_fields = ()

    def to_representation(self, instance):
        """Return only image information, not profile information"""
        if instance.proof_image:
            return ImageSerializer(instance.proof_image).data
        return None

    def create(self, validated_data):
        """Create or update profile proof image"""
        profile = validated_data.pop("profile")
        file = validated_data.pop("file")

        # 기존 proof_image가 있다면 재활용
        image, _ = Image.objects.update_or_create(
            owner=profile.user, image_type=ImageType.PROOF, defaults={"file": file}
        )

        profile.proof_image = image
        profile.save()

        return profile
