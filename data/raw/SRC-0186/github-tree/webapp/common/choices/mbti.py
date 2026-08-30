from django.db import models


class Mbti(models.TextChoices):
    ESTJ = "ESTJ", "ESTJ"
    ESTP = "ESTP", "ESTP"
    ESFJ = "ESFJ", "ESFJ"
    ESFP = "ESFP", "ESFP"
    ENFJ = "ENFJ", "ENFJ"
    ENFP = "ENFP", "ENFP"
    ENTJ = "ENTJ", "ENTJ"
    ENTP = "ENTP", "ENTP"
    ISTJ = "ISTJ", "ISTJ"
    ISTP = "ISTP", "ISTP"
    ISFJ = "ISFJ", "ISFJ"
    ISFP = "ISFP", "ISFP"
    INFJ = "INFJ", "INFJ"
    INFP = "INFP", "INFP"
    INTJ = "INTJ", "INTJ"
    INTP = "INTP", "INTP"
