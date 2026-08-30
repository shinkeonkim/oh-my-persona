from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from common.admin.ui_components import AdminScoreDisplay
from matchmakings.models import PreMatchingScore


class PreMatchingScoreInline(TabularInline):
  """PreMatching 상세 페이지에서 점수 인라인"""

  model = PreMatchingScore
  extra = 0
  fields = (
    "algorithm_category_display",
    "score_display",
    "created_at",
  )
  readonly_fields = (
    "algorithm_category_display",
    "score_display",
    "created_at",
  )

  def algorithm_category_display(self, obj):
    """알고리즘 카테고리 표시"""
    if obj.algorithm_category:
      return obj.get_algorithm_category_display()
    return "-"

  algorithm_category_display.short_description = "알고리즘"

  def score_display(self, obj):
    """점수 표시 (색상 포함)"""
    return AdminScoreDisplay.create(obj.score, show_bg=False)

  score_display.short_description = "점수"

  def has_add_permission(self, request, obj=None):
    """추가 권한 제한 (자동 생성되므로)"""
    return False

  def has_change_permission(self, request, obj=None):
    """수정 권한 제한"""
    return False

  def has_delete_permission(self, request, obj=None):
    """삭제 권한 제한"""
    return request.user.is_superuser


@admin.register(PreMatchingScore)
class PreMatchingScoreAdmin(ModelAdmin):
  """PreMatchingScore 관리 어드민"""

  list_display = (
    "id",
    "prematching_info",
    "algorithm_category",
    "score_display",
    "created_at",
    "updated_at",
  )
  list_filter = (
    ("algorithm_category", ChoicesDropdownFilter),
    "score",
    "created_at",
    "prematching__status",
    "prematching__male_user__profile__region",
    "prematching__female_user__profile__region",
  )
  search_fields = (
    "prematching__male_user__email",
    "prematching__male_user__username",
    "prematching__female_user__email",
    "prematching__female_user__username",
    "algorithm_category",
  )
  ordering = ("-created_at", )
  date_hierarchy = "created_at"
  autocomplete_fields = ("prematching", )
  readonly_fields = (
    "created_at",
    "updated_at",
  )

  fieldsets = (
    (
      "점수 정보",
      {
        "fields": (
          "prematching",
          "algorithm_category",
          "score",
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

  def prematching_info(self, obj):
    """PreMatching 정보"""
    if obj.prematching:
      return format_html(
        "<div>"
        "<strong>ID: {}</strong><br/>"
        "<small>남성: {} | 여성: {}</small><br/>"
        "<small>상태: {}</small>"
        "</div>",
        obj.prematching.id,
        obj.prematching.male_user.email if obj.prematching.male_user else "-",
        (obj.prematching.female_user.email if obj.prematching.female_user else "-"),
        obj.prematching.get_status_display(),
      )
    return "-"

  prematching_info.short_description = "매칭 정보"
  prematching_info.admin_order_field = "prematching__id"

  def score_display(self, obj):
    """점수 표시 (색상 포함)"""
    return AdminScoreDisplay.create(obj.score, show_bg=True)

  score_display.short_description = "점수"
  score_display.admin_order_field = "score"

  def get_queryset(self, request):
    queryset = super().get_queryset(request)
    return queryset.select_related(
      "prematching",
      "prematching__male_user",
      "prematching__female_user",
      "prematching__male_user__profile",
      "prematching__female_user__profile",
    )

  def has_add_permission(self, request):
    """추가 권한 제한 (자동 생성되므로)"""
    return False

  def has_delete_permission(self, request, obj=None):
    """삭제 권한 제한"""
    return request.user.is_superuser

  actions = ("recalculate_scores", )

  def recalculate_scores(self, request, queryset):
    """선택된 점수 재계산"""
    from matchmakings.tasks.pre_matching_task import calculate_pre_matching_score

    count = 0
    for score in queryset:
      calculate_pre_matching_score.delay(score.prematching.id, score.algorithm_category)
      count += 1

    self.message_user(request, f"{count}개의 점수 재계산을 요청했습니다.")
