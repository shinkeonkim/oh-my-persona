from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from disclosures.models import CompanyDisclosure
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
  RangeDateFilter,
)


@admin.register(CompanyDisclosure)
class CompanyDisclosureAdmin(ModelAdmin):
  list_display = (
    "id",
    "company",
    "title",
    "receipt_no",
    "published_at",
    "disclosure_type",
  )
  list_filter = (
    "disclosure_type",
    ["published_at", RangeDateFilter],
  )

  search_fields = ("title", "receipt_no", "company__name", "company__corp_code")
  readonly_fields = ("created_at", "updated_at", "html_preview")
  ordering = ("-published_at", )
  list_filter_submit = True
  list_filter_sheet = False

  fieldsets = (
    (
      _("Disclosure Details"),
      {
        "fields": (
          "company",
          "title",
          "receipt_no",
          "disclosure_type",
          "published_at",
          "source_url",
        )
      },
    ),
    (
      _("Content"),
      {
        "fields": ("text_body", "html_preview"),
      },
    ),
    (
      _("Meta"),
      {
        "fields": ("created_at", "updated_at"),
      },
    ),
  )

  def html_preview(self, obj):
    """HTML 본문을 렌더링하여 미리보기"""
    if not obj.html_body:
      return _("HTML 내용이 없습니다.")

    # iframe을 사용하여 안전하게 HTML 렌더링
    html_content = format_html(
      '<div style="border: 1px solid #ddd; padding: 10px; max-height: 600px; overflow: auto; background-color: white;">'
      '<iframe srcdoc="{}" style="width: 100%; min-height: 800px; border: none;"></iframe>'
      '</div>', obj.html_body.replace('"', '&quot;')
    )
    return mark_safe(html_content)

  html_preview.short_description = _("HTML 미리보기")
