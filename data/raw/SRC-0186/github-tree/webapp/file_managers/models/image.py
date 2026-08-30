import uuid

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from common.models import BaseModel, BaseModelManager, BaseModelQuerySet

User = get_user_model()

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "ico", "webp"]


class ImageType(models.TextChoices):
    PROFILE = "profile_images", "프로필 이미지"
    PROOF = "proof_images", "인증 사진"
    GENERAL = "images", "일반 이미지"


def rename_image(instance, filename):
    extension = filename.split(".")[-1]
    return f"{instance.image_type}/{uuid.uuid4()}.{extension}"


class ImageQuerySet(BaseModelQuerySet):
    pass


class ImageManager(BaseModelManager.from_queryset(ImageQuerySet)):
    pass


class Image(BaseModel):
    class Meta:
        db_table = "images"
        verbose_name = "Image"
        verbose_name_plural = "Images"

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
    )
    image_type = models.CharField(
        max_length=20,
        choices=ImageType.choices,
        default=ImageType.GENERAL,
        verbose_name="이미지 타입",
    )
    objects = ImageManager()
    file = models.ImageField(
        upload_to=rename_image,
        null=False,
        blank=False,
        verbose_name="File",
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS),
        ],
    )

    def __str__(self):
        return self.file.name

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super().delete(*args, **kwargs)
