from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
  AutocompleteSelectFilter,
  ChoicesDropdownFilter,
  RangeDateFilter,
)

from common.admin import AdminUserInfo
from common.choices.birth_time import BirthTime
from profiles.models import Gender, Profile

from .profile_image_inline import ProfileImageInline


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
  """프로필 관리 어드민"""

  list_display = (
    "id",
    "status",
    "user_info",
    "mbti",
    "gender",
    "birth_time_display",
    "introduction_preview",
    "is_intro_completed",
    "created_at",
    "updated_at",
  )
  list_filter = (
    ("status", ChoicesDropdownFilter),
    ("gender", ChoicesDropdownFilter),
    ("birth_time", ChoicesDropdownFilter),
    ("user", AutocompleteSelectFilter),
    ("job_info", AutocompleteSelectFilter),
    "region",
    "mbti",
    ("created_at", RangeDateFilter),
    ("updated_at", RangeDateFilter),
  )
  search_fields = (
    "user__email",
    "user__username",
    "mbti",
    "status",
    "region",
    "city",
    "gender",
    "job_info__job__name",
    "job_info__job_category__name",
    "job_info__manual_job",
    "job_info__manual_job_category",
    "introduction",
    "one_liner",
    "tmi",
  )
  list_filter_submit = True
  list_filter_sheet = False
  ordering = ("-created_at", )
  date_hierarchy = "created_at"
  autocomplete_fields = ("user", "job_info")
  inlines = (ProfileImageInline, )

  fieldsets = (
    (
      "사용자 정보",
      {
        "fields": ("user", ),
        "classes": ("wide", ),
      },
    ),
    (
      "개인 정보",
      {
        "fields": (
          "status",
          "mbti",
          "gender",
          "birth_time",
        ),
        "classes": ("wide", ),
      },
    ),
    (
      "위치 정보",
      {
        "fields": (
          "region",
          "city",
        ),
        "classes": ("wide", ),
      },
    ),
    (
      "직업 정보",
      {
        "fields": ("job_info", ),
        "classes": ("wide", ),
      },
    ),
    (
      "소개 정보",
      {
        "fields": (
          "introduction",
          "one_liner",
          "tmi",
        ),
        "classes": ("wide", ),
      },
    ),
    (
      "인증 정보",
      {
        "fields": (
          "proof_image",
          "proof_image_preview",
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

  readonly_fields = (
    "status",
    "created_at",
    "updated_at",
    "is_intro_completed",
    "proof_image_preview",
  )

  # Unfold 특화 설정
  list_per_page = 25
  show_full_result_count = True

  def user_info(self, obj):
    """사용자 정보 표시"""
    return AdminUserInfo.create(obj.user, show_email=True, show_status=True)

  user_info.short_description = "사용자 정보"
  user_info.admin_order_field = "user__username"

  def birth_time_display(self, obj):
    """출생시 표시"""
    return obj.get_birth_time_display() or "-"

  birth_time_display.short_description = "출생시"
  birth_time_display.admin_order_field = "birth_time"

  def introduction_preview(self, obj):
    """한줄 소개 미리보기"""
    if obj.introduction:
      return obj.introduction[:30] + "..." if len(obj.introduction) > 30 else obj.introduction
    return "-"

  introduction_preview.short_description = "한줄 소개"
  introduction_preview.admin_order_field = "introduction"

  def proof_image_preview(self, obj):
    """인증 사진 미리보기"""
    if obj and obj.proof_image and obj.proof_image.file:
      return format_html(
        '<img src="{}" style="max-width: 80px; max-height: 80px; object-fit: cover;' +
        'border-radius: 6px; border: 2px solid #e1e5e9;" />',
        obj.proof_image.file.url,
      )
    return format_html('<span style="color: #6c757d; font-style: italic;">인증 사진 없음</span>')

  proof_image_preview.short_description = "인증 사진"
  proof_image_preview.admin_order_field = "proof_image"

  def get_queryset(self, request):
    queryset = super().get_queryset(request)
    return queryset.select_related(
      "user",
      "job_info",
      "job_info__job",
      "job_info__job_category",
      "proof_image",
    )

  def formfield_for_choice_field(self, db_field, request, **kwargs):
    """선택 필드 커스터마이징"""
    if db_field.name == "gender":
      kwargs["choices"] = Gender.choices
    elif db_field.name == "birth_time":
      kwargs["choices"] = BirthTime.choices
    return super().formfield_for_choice_field(db_field, request, **kwargs)

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    """외래키 필드 커스터마이징"""
    return super().formfield_for_foreignkey(db_field, request, **kwargs)
