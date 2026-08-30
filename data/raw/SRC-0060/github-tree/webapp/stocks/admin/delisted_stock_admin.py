"""
Delisted Stock Admin
"""

import logging
from datetime import date

from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path, reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from stocks.models import DelistedStock
from stocks.views import DelistedStockIngestView
from unfold.admin import ModelAdmin
from unfold.decorators import action

logger = logging.getLogger(__name__)


@admin.register(DelistedStock)
class DelistedStockAdmin(ModelAdmin):
  list_display = [
    "isu_cd",
    "isu_nm",
    "market_display",
    "secugrp_nm",
    "list_dd",
    "delist_dd_colored",
    "delist_rsn_dsc_short",
    "created_at",
  ]
  list_filter = [
    "market",
    "secugrp_nm",
    "kind_stkcert_tp_nm",
    "delist_dd",
    "created_at",
  ]
  search_fields = [
    "isu_cd",
    "isu_nm",
    "delist_rsn_dsc",
    "to_isu_srt_cd",
    "to_isu_abbrv",
  ]
  readonly_fields = [
    "isu_cd",
    "isu_nm",
    "market",
    "secugrp_nm",
    "kind_stkcert_tp_nm",
    "list_dd",
    "delist_dd",
    "delist_rsn_dsc",
    "arrantrd_mktact_enforce_dd",
    "arrantrd_end_dd",
    "idx_ind_nm",
    "parval",
    "list_shrs",
    "to_isu_srt_cd",
    "to_isu_abbrv",
    "raw",
    "created_at",
    "updated_at",
  ]
  date_hierarchy = "delist_dd"
  ordering = ["-delist_dd", "isu_cd"]
  list_filter_submit = True
  list_filter_sheet = False

  # Changelist actions
  actions_list = ["test_ingest_action"]

  fieldsets = (
    (
      "기본 정보",
      {
        "fields": (
          "isu_cd",
          "isu_nm",
          "market",
          "secugrp_nm",
          "kind_stkcert_tp_nm",
        )
      },
    ),
    (
      "상장/폐지 정보",
      {
        "fields": (
          "list_dd",
          "delist_dd",
          "delist_rsn_dsc",
        )
      },
    ),
    (
      "정리매매 정보",
      {
        "fields": (
          "arrantrd_mktact_enforce_dd",
          "arrantrd_end_dd",
        )
      },
    ),
    (
      "기타 정보",
      {
        "fields": (
          "idx_ind_nm",
          "parval",
          "list_shrs",
          "to_isu_srt_cd",
          "to_isu_abbrv",
        )
      },
    ),
    (
      "메타 정보",
      {
        "fields": (
          "raw",
          "created_at",
          "updated_at",
        ),
        "classes": ("collapse", ),
      },
    ),
  )

  def delist_dd_colored(self, obj):
    """상장폐지일을 색상으로 표시"""
    if obj.delist_dd:
      days_until = (obj.delist_dd - date.today()).days
      if days_until < 0:
        color = "red"
        status = "폐지완료"
      elif days_until == 0:
        color = "orange"
        status = "오늘폐지"
      elif days_until <= 7:
        color = "orange"
        status = f"{days_until}일후"
      else:
        color = "green"
        status = f"{days_until}일후"
      return format_html(
        '<span style="color: {};">{} ({})</span>',
        color,
        obj.delist_dd,
        status,
      )
    return "-"

  delist_dd_colored.short_description = "상장폐지일"
  delist_dd_colored.admin_order_field = "delist_dd"

  def market_display(self, obj):
    """시장 정보 표시"""
    if obj.market:
      return f"{obj.market.name}"
    return "-"

  market_display.short_description = "시장"
  market_display.admin_order_field = "market"

  def delist_rsn_dsc_short(self, obj):
    """상장폐지 사유를 짧게 표시"""
    if obj.delist_rsn_dsc:
      max_length = 50
      if len(obj.delist_rsn_dsc) > max_length:
        return obj.delist_rsn_dsc[:max_length] + "..."
      return obj.delist_rsn_dsc
    return "-"

  delist_rsn_dsc_short.short_description = "상장폐지 사유"

  @action(
    description=_("테스트 수집"),
    url_path="test-ingest",
    permissions=["test_ingest_action"],
  )
  def test_ingest_action(self, request: HttpRequest):
    """Changelist에서 테스트 수집 페이지로 이동"""
    return redirect(reverse_lazy("admin:companies_delistedstock_ingest"))

  def has_test_ingest_action_permission(self, request: HttpRequest):
    """테스트 수집 액션 권한 체크"""
    # 스태프 권한이 있으면 표시
    return request.user.is_staff

  def get_urls(self):
    """커스텀 URL 추가"""
    urls = super().get_urls()
    custom_urls = [
      path(
        "ingest/",
        self.admin_site.admin_view(DelistedStockIngestView.as_view(model_admin=self)),
        name="companies_delistedstock_ingest",
      ),
    ]
    return custom_urls + urls

  def has_add_permission(self, request):
    """추가 권한 없음 (수집을 통해서만 생성)"""
    return False

  def has_delete_permission(self, request, obj=None):
    """삭제 권한 있음"""
    return True
