from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from common.models import BaseModel

from .referral import Referral

User = get_user_model()


class MatchingStatus(models.TextChoices):
    SENT = "sent"
    RECEIVED = "received"
    REJECTED = "rejected"
    EXPIRED = "expired"
    # TODO: 매칭 만료 처리 작업 필요


class Matching(BaseModel):
    class Meta:
        db_table = "matchings"
        verbose_name = "Matching"
        verbose_name_plural = "Matchings"
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"],
                name="unique_sender_receiver",
            )
        ]

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="matchings_sent",
        verbose_name="매칭 요청자",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="matchings_received",
        verbose_name="매칭 수신자",
    )
    ticket_amount = models.PositiveIntegerField(
        verbose_name="사용된 티켓 수량", help_text="해당 매칭을 통해 사용된 티켓의 수"
    )
    sent_at = models.DateTimeField(verbose_name="전송 일시")
    received_at = models.DateTimeField(null=True, blank=True, verbose_name="수신 일시")
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name="거절 일시")
    expired_at = models.DateTimeField(null=True, blank=True, verbose_name="만료된 일시")

    # 추천 현황과의 연결
    referral = models.ForeignKey(
        Referral,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matchings",
        verbose_name="추천 현황",
    )

    @property
    def status(self):
        if self.rejected_at:
            return MatchingStatus.REJECTED
        elif self.received_at:
            return MatchingStatus.RECEIVED
        else:
            return MatchingStatus.SENT

    def clean(self):
        super().clean()

        # sender와 receiver의 성별이 있어야 함
        sender_gender = self.sender.profile.gender if hasattr(self.sender, "profile") else None
        receiver_gender = self.receiver.profile.gender if hasattr(self.receiver, "profile") else None

        if not sender_gender:
            raise ValidationError({"sender": "매칭 요청자의 성별이 없습니다."})

        if not receiver_gender:
            raise ValidationError({"receiver": "매칭 수신자의 성별이 없습니다."})

        if sender_gender == receiver_gender:
            raise ValidationError({"receiver": "매칭 요청자와 수신자의 성별이 달라야 합니다."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.sent_at})"

    def accept(self):
        self.received_at = timezone.now()
        self.rejected_at = None
        self.save()

    def reject(self):
        self.rejected_at = timezone.now()
        self.received_at = None
        self.save()

    def expire(self):
        self.expired_at = timezone.now()
        self.save()
