from django.contrib.auth.models import (
  AbstractBaseUser,
  BaseUserManager,
  PermissionsMixin,
)
from django.db import models

from common.models import BaseModel, BaseModelManager, BaseModelQuerySet


class UserQuerySet(BaseModelQuerySet):

  def active(self):
    return self.filter(is_active=True)

  def staff(self):
    return self.filter(is_staff=True)

  def superusers(self):
    return self.filter(is_superuser=True)


class UserManager(BaseModelManager.from_queryset(UserQuerySet), BaseUserManager):

  def create_user(self, email, password=None, **extra_fields):
    """주어진 이메일과 비밀번호로 유저를 생성하고 저장합니다."""

    if not email:
      raise ValueError("Email is required")

    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)

    user.save(using=self._db)
    return user

  def create_superuser(self, email, password=None, **extra_fields):
    extra_fields.setdefault("is_staff", True)
    extra_fields.setdefault("is_superuser", True)
    return self.create_user(email, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):

  class Meta:
    db_table = "users"
    verbose_name = "User"
    verbose_name_plural = "Users"

  objects = UserManager()

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["username"]

  email = models.EmailField(unique=True)
  username = models.CharField(max_length=20)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
