from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
  AutocompleteSelectFilter,
  DropdownFilter,
  RangeDateFilter,
)

from common.admin.ui_components import AdminBadge, AdminUserInfo
from matchmakings.models import Matching


class MatchingStatusFilter(DropdownFilter):
  title = _("매칭 상태")
  parameter_name = "status"

  def lookups(self, request, model_admin):
    return (
      ("sent", _("전송됨")),
      ("received", _("수신됨")),
      ("rejected", _("거절됨")),
    )

  def queryset(self, request, queryset):
    if self.value() == "sent":
      return queryset.filter(received_at__isnull=True, rejected_at__isnull=True)
    if self.value() == "received":
      return queryset.filter(received_at__isnull=False, rejected_at__isnull=True)
    if self.value() == "rejected":
      return queryset.filter(rejected_at__isnull=False)
    return queryset


@admin.register(Matching)
class MatchingAdmin(ModelAdmin):
  """Matching 관리 어드민"""

  list_display = (
    "id",
    "sender_info",
    "receiver_info",
    "status_badge",
    "ticket_amount",
    "sent_at",
    "received_at",
    "rejected_at",
  )
  list_filter = (
    MatchingStatusFilter,
    ("sent_at", RangeDateFilter),
    ("received_at", RangeDateFilter),
    ("rejected_at", RangeDateFilter),
    ("sender", AutocompleteSelectFilter),
    ("receiver", AutocompleteSelectFilter),
  )
  search_fields = (
    "sender__email",
    "sender__username",
    "receiver__email",
    "receiver__username",
  )
  list_filter_submit = True
  list_filter_sheet = False
  autocomplete_fields = ("sender", "receiver")
  ordering = ("-sent_at", )
  date_hierarchy = "sent_at"
  readonly_fields = (
    "created_at",
    "updated_at",
  )

  fieldsets = (
    (
      "매칭 정보",
      {
        "fields": (
          "sender",
          "receiver",
          "ticket_amount",
        ),
        "classes": ("wide", ),
      },
    ),
    (
      "매칭 상태",
      {
        "fields": (
          "sent_at",
          "received_at",
          "rejected_at",
        ),
        "classes": ("wide", ),
      },
    ),
    (
      "추천 정보",
      {
        "fields": ("referral", ),
        "classes": ("wide", ),
      },
    ),
    (
      "시스템 정보",
      {
        "fields": (
          "created_at",
          "updated_at",
        ),
        "classes": ("collapse", ),
      },
    ),
  )

  list_per_page = 25
  show_full_result_count = True

  def sender_info(self, obj):
    """매칭 요청자 정보"""
    return AdminUserInfo.create(obj.sender, show_status=False)

  sender_info.short_description = "요청자"
  sender_info.admin_order_field = "sender__email"

  def receiver_info(self, obj):
    """매칭 수신자 정보"""
    return AdminUserInfo.create(obj.receiver, show_status=False)

  receiver_info.short_description = "수신자"
  receiver_info.admin_order_field = "receiver__email"

  def status_badge(self, obj):
    """매칭 상태 배지"""
    if obj.rejected_at:
      return AdminBadge.danger("거절됨")
    elif obj.received_at:
      return AdminBadge.success("수신됨")
    else:
      return AdminBadge.info("전송됨")

  status_badge.short_description = "상태"
  status_badge.admin_order_field = "sent_at"

  def get_queryset(self, request):
    queryset = super().get_queryset(request)
    return queryset.select_related(
      "sender",
      "receiver",
      "sender__profile",
      "receiver__profile",
      "referral",
    )

  def has_add_permission(self, request):
    """추가 권한 제한 (자동 생성되므로)"""
    return False

  def has_delete_permission(self, request, obj=None):
    """삭제 권한 제한"""
    return request.user.is_superuser

  actions = ("mark_as_received", "mark_as_rejected")
