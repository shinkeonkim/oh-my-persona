from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from common.models import BaseModel, BaseModelManager, BaseModelQuerySet
from users.validators import validate_username


class UserQuerySet(BaseModelQuerySet):
    def active(self):
        return self.filter(is_active=True)

    def staff(self):
        return self.filter(is_staff=True)

    def superusers(self):
        return self.filter(is_superuser=True)


class UserManager(BaseModelManager.from_queryset(UserQuerySet), BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        """주어진 username과 비밀번호로 유저를 생성하고 저장합니다."""

        if not username:
            raise ValueError("Username is required")

        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)

        user = self.model(username=username, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    username = models.CharField(
        max_length=20,
        unique=True,
        validators=[validate_username],
        help_text="4자리 이상의 영문과 숫자 조합",
    )
    email = models.EmailField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
