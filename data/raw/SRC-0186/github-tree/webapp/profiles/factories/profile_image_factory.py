"""
ProfileImage Factory 클래스
"""

from django.core.files.uploadedfile import SimpleUploadedFile

import factory
from factory.django import DjangoModelFactory

from file_managers.models import Image, ImageType
from profiles.models import ProfileImage

from .profile_factory import ProfileFactory


class ProfileImageFactory(DjangoModelFactory):
    """ProfileImage Factory"""

    class Meta:
        model = ProfileImage

    profile = factory.SubFactory(ProfileFactory)
    image = factory.LazyAttribute(
        lambda obj: Image.objects.create(
            owner=obj.profile.user if obj.profile else None,
            image_type=ImageType.PROFILE,
            file=SimpleUploadedFile(
                name=f"test_image_{factory.Faker('uuid4')}.jpg",
                content=b"fake image content",
                content_type="image/jpeg",
            ),
        )
    )

    class Params:
        # 트레이트: 인증 사진
        proof_image = factory.Trait(
            image=factory.LazyAttribute(
                lambda obj: Image.objects.create(
                    owner=obj.profile.user if obj.profile else None,
                    image_type=ImageType.PROOF,
                    file=SimpleUploadedFile(
                        name=f"proof_image_{factory.Faker('uuid4')}.jpg",
                        content=b"fake proof image content",
                        content_type="image/jpeg",
                    ),
                )
            )
        )

        # 트레이트: 일반 이미지
        general_image = factory.Trait(
            image=factory.LazyAttribute(
                lambda obj: Image.objects.create(
                    owner=obj.profile.user if obj.profile else None,
                    image_type=ImageType.GENERAL,
                    file=SimpleUploadedFile(
                        name=f"general_image_{factory.Faker('uuid4')}.jpg",
                        content=b"fake general image content",
                        content_type="image/jpeg",
                    ),
                )
            )
        )
