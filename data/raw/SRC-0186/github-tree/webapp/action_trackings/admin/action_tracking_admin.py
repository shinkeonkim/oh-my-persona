from django.contrib import admin

from action_trackings.models import ActionTracking
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
  AutocompleteSelectFilter,
  ChoicesDropdownFilter,
  RangeDateFilter,
  RelatedDropdownFilter,
)
from unfold.paginator import InfinitePaginator


@admin.register(ActionTracking)
class ActionTrackingAdmin(ModelAdmin):
  """액션 트래킹 Admin"""

  list_display = [
    "id",
    "user",
    "action_type",
    "content_type",
    "object_id",
    "ip_address",
    "created_at",
  ]
  list_filter = [
    ("action_type", ChoicesDropdownFilter),
    ("created_at", RangeDateFilter),
    ("user", AutocompleteSelectFilter),
    ("content_type", RelatedDropdownFilter),
  ]
  search_fields = [
    "user__email",
    "user__username",
    "ip_address",
  ]
  list_filter_submit = True
  list_filter_sheet = False
  autocomplete_fields = ["user"]
  readonly_fields = [
    "id",
    "user",
    "action_type",
    "content_type",
    "object_id",
    "content_object",
    "metadata",
    "ip_address",
    "user_agent",
    "created_at",
    "updated_at",
  ]
  date_hierarchy = "created_at"
  ordering = ["-created_at"]

  # InfinitePaginator for large datasets
  paginator = InfinitePaginator
  show_full_result_count = False

  def has_add_permission(self, request):
    """추가 권한 비활성화 (트래킹은 자동으로만 생성)"""
    return False

  def has_change_permission(self, request, obj=None):
    """수정 권한 비활성화 (읽기 전용)"""
    return False

  def has_delete_permission(self, request, obj=None):
    """삭제 권한은 관리자만 가능"""
    return request.user.is_superuser
