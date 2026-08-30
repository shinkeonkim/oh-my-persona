from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from profiles.models import JobCategory


class JobCategoryResource(resources.ModelResource):
  """JobCategory 모델을 위한 import/export 리소스"""

  class Meta:
    model = JobCategory
    fields = ("id", "name", "created_at", "updated_at")
    export_order = ("id", "name", "created_at", "updated_at")
    import_id_fields = ("id", )
    skip_unchanged = True
    report_skipped = False


@admin.register(JobCategory)
class JobCategoryAdmin(ModelAdmin, ImportExportModelAdmin):
  """직업 카테고리 관리 어드민"""

  # Import/Export 설정
  resource_class = JobCategoryResource
  import_form_class = ImportForm
  export_form_class = ExportForm

  list_display = (
    "id",
    "name",
    "job_count",
    "profile_count",
    "created_at",
    "updated_at",
  )
  list_filter = (
    "created_at",
    "updated_at",
  )
  search_fields = ("name", )
  ordering = ("name", )
  date_hierarchy = "created_at"

  fieldsets = (
    (
      "카테고리 정보",
      {
        "fields": ("name", ),
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
    "created_at",
    "updated_at",
    "job_count",
    "profile_count",
  )

  # Unfold 특화 설정
  list_per_page = 25
  show_full_result_count = True
  list_filter_submit = True
  list_filter_sheet = False

  def job_count(self, obj):
    """해당 카테고리의 직업 수"""
    return obj.job_set.count()

  job_count.short_description = "직업 수"
  job_count.admin_order_field = "job_count"

  def profile_count(self, obj):
    """해당 카테고리의 직업을 가진 프로필 수"""
    from profiles.models import JobInfo

    return JobInfo.objects.filter(job__job_category=obj).count()

  profile_count.short_description = "프로필 수"
  profile_count.admin_order_field = "profile_count"

  def get_queryset(self, request):
    queryset = super().get_queryset(request)
    return queryset
