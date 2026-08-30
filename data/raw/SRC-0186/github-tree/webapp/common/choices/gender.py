from django.db import models


class Gender(models.TextChoices):
    MALE = "M"
    FEMALE = "F"
