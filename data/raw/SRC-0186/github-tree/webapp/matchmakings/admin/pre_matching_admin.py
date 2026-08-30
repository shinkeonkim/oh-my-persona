from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin

from common.admin.ui_components import (
  AdminBadge,
  AdminDescriptionPreview,
  AdminUserInfo,
)
from matchmakings.admin.pre_matching_score_admin import PreMatchingScoreInline
from matchmakings.models import PreMatching, PreMatchingStatus


class PreMatchingStatusFilter(admin.SimpleListFilter):
  title = _("매칭 상태")
  parameter_name = "status"

  def lookups(self, request, model_admin):
    return (
      ("pending", _("대기 중")),
      ("calculating", _("계산 중")),
      ("completed", _("완료")),
      ("recommended", _("추천됨")),
    )

  def queryset(self, request, queryset):
    if self.value() == "pending":
      return queryset.filter(status=PreMatchingStatus.PENDING)
    if self.value() == "calculating":
      return queryset.filter(status=PreMatchingStatus.CALCULATING)
    if self.value() == "completed":
      return queryset.filter(status=PreMatchingStatus.COMPLETED)
    if self.value() == "recommended":
      return queryset.filter(status=PreMatchingStatus.RECOMMENDED)
    return queryset


@admin.register(PreMatching)
class PreMatchingAdmin(ModelAdmin):
  """PreMatching 관리 어드민"""

  list_display = (
    "id",
    "male_user_info",
    "female_user_info",
    "status_badge",
    "last_calculated_at",
  )
  list_filter = (
    PreMatchingStatusFilter,
    "last_calculated_at",
  )
  search_fields = (
    "male_user__email",
    "male_user__username",
    "female_user__email",
    "female_user__username",
    "matching_reason",
  )
  ordering = ("-created_at", )
  date_hierarchy = "created_at"
  inlines = (PreMatchingScoreInline, )
  readonly_fields = (
    "created_at",
    "updated_at",
    "last_calculated_at",
  )

  fieldsets = (
    (
      "매칭 정보",
      {
        "fields": (
          "male_user",
          "female_user",
          "status",
        ),
        "classes": ("wide", ),
      },
    ),
    (
      "매칭 상세",
      {
        "fields": (
          "matching_reason",
          "last_calculated_at",
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

  def male_user_info(self, obj):
    """남성 유저 정보"""
    return AdminUserInfo.create(obj.male_user)

  male_user_info.short_description = "남성 유저"
  male_user_info.admin_order_field = "male_user__email"

  def female_user_info(self, obj):
    """여성 유저 정보"""
    return AdminUserInfo.create(obj.female_user)

  female_user_info.short_description = "여성 유저"
  female_user_info.admin_order_field = "female_user__email"

  def status_badge(self, obj):
    """상태 배지"""
    status_colors = {
      PreMatchingStatus.PENDING: ("gray", "#6c757d"),
      PreMatchingStatus.CALCULATING: ("blue", "#17a2b8"),
      PreMatchingStatus.COMPLETED: ("green", "#28a745"),
      PreMatchingStatus.RECOMMENDED: ("purple", "#6f42c1"),
    }

    color, bg_color = status_colors.get(obj.status, ("gray", "#6c757d"))
    status_display = dict(PreMatchingStatus.choices).get(obj.status, obj.status)

    return AdminBadge.create(status_display, "white", bg_color)

  status_badge.short_description = "상태"
  status_badge.admin_order_field = "status"

  def matching_reason_preview(self, obj):
    """매칭 사유 미리보기"""
    return AdminDescriptionPreview.create(obj.matching_reason, max_length=50)

  matching_reason_preview.short_description = "매칭 사유"

  def get_queryset(self, request):
    queryset = super().get_queryset(request)
    return queryset.select_related(
      "male_user",
      "female_user",
      "male_user__profile",
      "female_user__profile",
    )

  def has_add_permission(self, request):
    """추가 권한 제한 (자동 생성되므로)"""
    return False

  def has_delete_permission(self, request, obj=None):
    """삭제 권한 제한"""
    return request.user.is_superuser

  actions = (
    "mark_as_pending",
    "mark_as_completed",
    "mark_as_recommended",
    "recalculate_prematching_scores",
  )

  def mark_as_pending(self, request, queryset):
    """선택된 매칭을 대기 상태로 변경"""
    updated = queryset.update(status=PreMatchingStatus.PENDING)
    self.message_user(request, f"{updated}개의 매칭을 대기 상태로 변경했습니다.")

  def mark_as_completed(self, request, queryset):
    """선택된 매칭을 완료 상태로 변경"""
    updated = queryset.update(status=PreMatchingStatus.COMPLETED)
    self.message_user(request, f"{updated}개의 매칭을 완료 상태로 변경했습니다.")

  def mark_as_recommended(self, request, queryset):
    """선택된 매칭을 추천 상태로 변경"""
    updated = queryset.update(status=PreMatchingStatus.RECOMMENDED)
    self.message_user(request, f"{updated}개의 매칭을 추천 상태로 변경했습니다.")

  def recalculate_prematching_scores(self, request, queryset):
    """선택된 매칭들의 점수를 다시 계산"""
    from matchmakings.tasks.pre_matching_task import (
      calculate_all_pre_matching_scores,
    )

    # 선택된 PreMatching들의 상태를 PENDING으로 변경하고 점수 재계산 task 실행
    task_count = 0
    for prematching in queryset:
      try:
        # 상태를 PENDING으로 변경
        prematching.status = PreMatchingStatus.PENDING
        prematching.save()

        # 점수 재계산 task 실행
        calculate_all_pre_matching_scores.delay(prematching.id)
        task_count += 1
      except Exception as e:
        self.message_user(
          request,
          f"매칭 {prematching.id}에 대한 task 실행 실패: {str(e)}",
          level="error",
        )

    self.message_user(
      request,
      f"{task_count}개의 매칭에 대해 점수 재계산 task를 실행했습니다. "
      "결과는 Celery worker가 처리한 후 확인할 수 있습니다.",
      level="success",
    )
