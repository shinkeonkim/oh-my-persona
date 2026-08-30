from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from profiles.models import Address


class AddressResource(resources.ModelResource):
  """Address 모델을 위한 import/export 리소스"""

  class Meta:
    model = Address
    fields = ("id", "region", "city", "created_at", "updated_at")
    export_order = ("id", "region", "city", "created_at", "updated_at")
    import_id_fields = ("id", )
    skip_unchanged = True
    report_skipped = False


@admin.register(Address)
class AddressAdmin(ModelAdmin, ImportExportModelAdmin):
  """주소 관리 어드민"""

  # Import/Export 설정
  resource_class = AddressResource
  import_form_class = ImportForm
  export_form_class = ExportForm

  list_display = (
    "id",
    "region",
    "city",
  )
  list_filter = ("region", )
  search_fields = (
    "region",
    "city",
  )
  ordering = ("-created_at", )
  date_hierarchy = "created_at"

  fieldsets = (
    (
      "주소 정보",
      {
        "fields": (
          "region",
          "city",
        ),
        "classes": ("collapse", ),
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
  )

  # Unfold 특화 설정
  list_per_page = 25
  show_full_result_count = True
  list_filter_submit = True
  list_filter_sheet = False

  def get_queryset(self, request):
    queryset = super().get_queryset(request)
    return queryset.select_related()
