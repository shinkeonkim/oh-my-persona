from django.contrib import admin

from unfold.admin import ModelAdmin

from companies.models import CompanyIndustry


@admin.register(CompanyIndustry)
class CompanyIndustryAdmin(ModelAdmin):
  list_display = ("name", "created_at", "updated_at")
  search_fields = ("name", )
  ordering = ("name", )
  list_filter_submit = True
  list_filter_sheet = False
