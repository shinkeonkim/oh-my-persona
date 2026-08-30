from django.contrib import admin

from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from profiles.models import Job, JobCategory


class JobResource(resources.ModelResource):
  """Job 모델을 위한 import/export 리소스"""

  job_category = fields.Field(
    column_name="job_category_name",
    attribute="job_category",
    widget=ForeignKeyWidget(JobCategory, "name"),
  )

  class Meta:
    model = Job
    fields = ("id", "name", "job_category", "created_at", "updated_at")
    export_order = ("id", "name", "job_category_name", "created_at", "updated_at")
    import_id_fields = ("id", )
    skip_unchanged = True
    report_skipped = False


@admin.register(Job)
class JobAdmin(ModelAdmin, ImportExportModelAdmin):
  """직업 관리 어드민"""

  # Import/Export 설정
  resource_class = JobResource
  import_form_class = ImportForm
  export_form_class = ExportForm

  list_display = (
    "id",
    "name",
    "job_category",
    "profile_count",
    "created_at",
    "updated_at",
  )
  list_filter = (
    "job_category",
    "created_at",
    "updated_at",
  )
  search_fields = (
    "name",
    "job_category__name",
  )
  ordering = ("job_category", "name")
  date_hierarchy = "created_at"
  autocomplete_fields = ("job_category", )

  fieldsets = (
    (
      "직업 정보",
      {
        "fields": (
          "name",
          "job_category",
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
    "created_at",
    "updated_at",
    "profile_count",
  )

  # Unfold 특화 설정
  list_per_page = 25
  show_full_result_count = True
  list_filter_submit = True
  list_filter_sheet = False

  def profile_count(self, obj):
    """해당 직업을 가진 프로필 수 (JobInfo를 통해)"""
    from profiles.models import JobInfo

    return JobInfo.objects.filter(job=obj).count()

  profile_count.short_description = "프로필 수"
  profile_count.admin_order_field = "profile_count"

  def get_queryset(self, request):
    queryset = super().get_queryset(request)
    return queryset.select_related("job_category")
