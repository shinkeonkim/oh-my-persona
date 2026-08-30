from django.contrib import admin

from unfold.admin import ModelAdmin

from common.admin.ui_components import AdminUserInfo
from matchmakings.models import ReferralLog


@admin.register(ReferralLog)
class ReferralLogAdmin(ModelAdmin):
  """ReferralLog 관리 어드민"""

  list_display = (
    "id",
    "user_info",
    "referral_user_info",
    "referred_at",
    "created_at",
  )
  list_filter = (
    "referred_at",
    "user__profile__gender",
    "referral_user__profile__gender",
  )
  search_fields = (
    "user__email",
    "user__username",
    "referral_user__email",
    "referral_user__username",
  )
  ordering = ("-referred_at", )
  date_hierarchy = "referred_at"
  readonly_fields = (
    "created_at",
    "updated_at",
  )

  fieldsets = (
    (
      "추천 정보",
      {
        "fields": (
          "referral",
          "user",
          "referral_user",
          "referred_at",
        ),
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
  list_filter_submit = True
  list_filter_sheet = False

  def user_info(self, obj):
    """추천을 받은 사용자 정보"""
    return AdminUserInfo.create(obj.user, show_status=False)

  user_info.short_description = "추천 받은 사용자"
  user_info.admin_order_field = "user__email"

  def referral_user_info(self, obj):
    """추천된 사용자 정보"""
    return AdminUserInfo.create(obj.referral_user, show_status=False)

  referral_user_info.short_description = "추천된 사용자"
  referral_user_info.admin_order_field = "referral_user__email"

  def get_queryset(self, request):
    queryset = super().get_queryset(request)
    return queryset.select_related(
      "user",
      "referral_user",
      "user__profile",
      "referral_user__profile",
      "referral",
    )

  def has_add_permission(self, request):
    """추가 권한 제한 (자동 생성되므로)"""
    return False

  def has_delete_permission(self, request, obj=None):
    """삭제 권한 제한"""
    return request.user.is_superuser
