from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin, TabularInline

from common.admin.ui_components import AdminUserInfo
from matchmakings.models import (
  Referral,
  ReferralCompatibilityTag,
  ReferralConversation,
  ReferralOverallOpinion,
  ReferralSynergy,
)


class ReferralCompatibilityTagInline(TabularInline):
  """Referral Compatibility Tag Inline"""

  model = ReferralCompatibilityTag
  extra = 0
  can_delete = True

  fields = ("compatibility_tag", )
  autocomplete_fields = ("compatibility_tag", )


class ReferralConversationInline(TabularInline):
  """Referral Conversation Inline"""

  model = ReferralConversation
  extra = 0
  can_delete = False

  fields = ("formatted_conversation", )
  readonly_fields = ("formatted_conversation", )

  def formatted_conversation(self, obj):
    """대화 내용을 보기 좋게 포맷"""
    if not obj or not obj.conversation_messages:
      return "-"

    messages = obj.conversation_messages
    html_parts = ['<div style="font-family: monospace; white-space: pre-wrap;">']

    for msg in messages:
      role = msg.get("role", "")
      content = msg.get("content", "")
      role_label = "캐릭터" if role == "CHARACTER" else "사용자"
      html_parts.append(f'<strong>[{role_label}]</strong> {content}<br><br>')

    html_parts.append("</div>")
    return format_html("".join(html_parts))

  formatted_conversation.short_description = "대화 내용"

  def has_add_permission(self, request, obj=None):
    """추가 권한 제한"""
    return False


class ReferralOverallOpinionInline(TabularInline):
  """Referral Overall Opinion Inline"""

  model = ReferralOverallOpinion
  extra = 0
  can_delete = False

  fields = (
    "generation_status",
    "opinion_for_male",
    "opinion_for_female",
    "error_message",
  )
  readonly_fields = (
    "generation_status",
    "opinion_for_male",
    "opinion_for_female",
    "error_message",
  )

  def has_add_permission(self, request, obj=None):
    """추가 권한 제한"""
    return False


class ReferralSynergyInline(TabularInline):
  """Referral Synergy Inline"""

  model = ReferralSynergy
  extra = 0
  can_delete = False

  fields = (
    "generation_status",
    "title",
    "description",
    "error_message",
  )
  readonly_fields = (
    "generation_status",
    "title",
    "description",
    "error_message",
  )

  def has_add_permission(self, request, obj=None):
    """추가 권한 제한"""
    return False


@admin.register(Referral)
class ReferralAdmin(ModelAdmin):
  """Referral 관리 어드민"""

  inlines = [
    ReferralCompatibilityTagInline,
    ReferralConversationInline,
    ReferralOverallOpinionInline,
    ReferralSynergyInline,
  ]

  list_display = (
    "id",
    "user_info",
    "referral_user_info",
    "referred_at",
    "created_at",
  )
  list_filter = (
    "referred_at",
    "user__profile__region",
    "referral_user__profile__region",
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
    ).prefetch_related("matchings")

  def has_add_permission(self, request):
    """추가 권한 제한 (자동 생성되므로)"""
    return False

  def has_delete_permission(self, request, obj=None):
    """삭제 권한 제한"""
    return request.user.is_superuser
