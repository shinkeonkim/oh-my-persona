from django.utils.html import format_html

from unfold.admin import TabularInline

from profiles.models import ProfileImage


class ProfileImageInline(TabularInline):
    model = ProfileImage
    extra = 1
    fields = ("image_preview", "image")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        """이미지 미리보기"""
        if obj and obj.image and obj.image.file:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: cover; border-radius: 4px;" />',
                obj.image.file.url,
            )
        return "이미지 없음"

    image_preview.short_description = "미리보기"
