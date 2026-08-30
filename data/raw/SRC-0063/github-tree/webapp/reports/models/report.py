from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from reports.choices import ReportStatusChoice

from common.models import BaseModel, BaseModelManager

User = get_user_model()


class ReportManager(BaseModelManager):
    def get_or_create_for_user_child(self, user, child):
        """사용자와 아동에 대한 레포트 조회 또는 생성"""
        report, created = self.get_or_create(
            user=user,
            child=child,
        )
        return report, created


class Report(BaseModel):
    """
    레포트 모델
    사용자와 아동당 1개만 존재하며, 게임 결과를 종합한 레포트
    """

    class Meta:
        db_table = "reports"
        verbose_name = _("레포트")
        verbose_name_plural = _("레포트")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "child"],
                name="unique_user_child_report",
            ),
        ]
        ordering = ["-updated_at"]

    objects = ReportManager()

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports",
        null=False,
        blank=False,
        verbose_name=_("사용자"),
    )
    child = models.ForeignKey(
        "users.Child",
        on_delete=models.CASCADE,
        related_name="reports",
        null=False,
        blank=False,
        verbose_name=_("아동"),
    )
    concentration_score = models.PositiveSmallIntegerField(
        null=False,
        blank=False,
        default=0,
        verbose_name=_("집중력 점수"),
        help_text="아동의 집중력 점수 (0-100)",
    )
    status = models.CharField(
        max_length=20,
        choices=ReportStatusChoice.choices,
        default=ReportStatusChoice.NO_GAMES_PLAYED,
        null=False,
        blank=False,
        verbose_name=_("상태"),
        help_text="레포트의 현재 상태",
    )

    def __str__(self):
        return f"{self.user.username} - {self.child.name} 레포트"
