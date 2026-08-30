from django.db import models

from common.models import BaseModel

from .watchlist import Watchlist


class WatchlistItem(BaseModel):

  class Meta:
    db_table = "watchlist_items"
    verbose_name = "Watchlist Item"
    verbose_name_plural = "Watchlist Items"

  watchlist = models.ForeignKey(
    Watchlist,
    on_delete=models.CASCADE,
    related_name="items",
    verbose_name="관심목록",
  )
  stock = models.ForeignKey(
    "stocks.Stock",
    on_delete=models.CASCADE,
    related_name="watchlist_items",
    verbose_name="주식",
  )
  notes = models.TextField(
    blank=True,
    null=True,
    verbose_name="메모",
  )

  def __str__(self) -> str:
    return f"WatchlistItem: {self.watchlist.name} - {self.stock.name}"
