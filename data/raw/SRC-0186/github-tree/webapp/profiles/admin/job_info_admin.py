from django.contrib import admin

from unfold.admin import ModelAdmin

from profiles.models import JobInfo


@admin.register(JobInfo)
class JobInfoAdmin(ModelAdmin):
  """프로필 직업 정보 관리 어드민"""

  list_display = ("id", "job", "job_category", "manual_job", "manual_job_category")
  search_fields = (
    "job__name",
    "job_category__name",
    "manual_job",
    "manual_job_category",
  )
  autocomplete_fields = ("job", "job_category")
  list_filter_submit = True
  list_filter_sheet = False

  def get_queryset(self, request):
    return super().get_queryset(request).select_related("job", "job_category")
