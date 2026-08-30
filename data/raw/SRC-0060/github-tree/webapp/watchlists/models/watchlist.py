from django.contrib.auth import get_user_model
from django.db import models

from common.models import BaseModel

User = get_user_model()


class Watchlist(BaseModel):

  class Meta:
    db_table = "watchlists"
    verbose_name = "Watchlist"
    verbose_name_plural = "Watchlists"

  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="watchlists",
    verbose_name="사용자",
  )

  name = models.CharField(max_length=255, verbose_name="관심목록명")
  description = models.TextField(blank=True, null=True, verbose_name="설명")

  def __str__(self) -> str:
    return f"Watchlist: {self.name} ({self.user.username})"
