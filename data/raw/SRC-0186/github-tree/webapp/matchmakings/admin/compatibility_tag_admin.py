from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from unfold.admin import ModelAdmin

from matchmakings.models import CompatibilityTag


@admin.register(CompatibilityTag)
class CompatibilityTagAdmin(ModelAdmin):
  """CompatibilityTag 관리 어드민"""

  list_display = (
    "id",
    "name",
    "usage_count",
    "created_at",
    "updated_at",
  )
  list_filter = ("created_at", )
  search_fields = ("name", )
  ordering = ("-created_at", )
  date_hierarchy = "created_at"
  readonly_fields = (
    "created_at",
    "updated_at",
    "display_prepared_compatibility_tags",
  )

  fieldsets = (
    (
      "태그 정보",
      {
        "fields": ("name", ),
        "classes": ("wide", ),
      },
    ),
    (
      "사용 정보",
      {
        "fields": ("display_prepared_compatibility_tags", ),
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

  def usage_count(self, obj):
    """사용 횟수"""
    return f"{obj.prepared_tags_count}개"

  usage_count.short_description = "사용 횟수"

  def display_prepared_compatibility_tags(self, obj):
    """이 태그를 사용하는 PreparedCompatibilityTag 목록"""
    prepared_tags = obj.prepared_compatibility_tags.all()[:50]  # 최대 50개만 표시

    if not prepared_tags:
      return "사용되지 않음"

    # 일주 조합 리스트 생성
    ilju_list = []
    for tag in prepared_tags:
      male_ilju = f"{tag.male_d_stem}{tag.male_d_branch}"
      female_ilju = f"{tag.female_d_stem}{tag.female_d_branch}"
      ilju_list.append(f"남자:{male_ilju} / 여자:{female_ilju}")

    total_count = obj.prepared_tags_count
    result = "<br>".join(ilju_list)

    if total_count > 50:
      result += f"<br><br><strong>... 외 {total_count - 50}개 더</strong>"

    result = f"<strong>총 {total_count}개의 일주 조합에서 사용됨</strong><br><br>{result}"

    return format_html(result)

  display_prepared_compatibility_tags.short_description = "사용되는 일주 조합"

  def get_queryset(self, request):
    queryset = super().get_queryset(request)
    return queryset.prefetch_related("prepared_compatibility_tags").annotate(
      prepared_tags_count=Count('prepared_compatibility_tags'))
