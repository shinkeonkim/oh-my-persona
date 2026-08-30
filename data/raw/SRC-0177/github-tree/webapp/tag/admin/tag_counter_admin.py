from django.contrib import admin
from tag.models import TagCounter


@admin.register(TagCounter)
class TagCounterAdmin(admin.ModelAdmin):
    list_display = (
        "tag",
        "memes_count",
        "bookmarkings_count",
        "created_at",
        "updated_at",
    )
    search_fields = ("tag__name",)
    readonly_fields = (
        "memes_count",
        "bookmarkings_count",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("tag")

    actions = ["reset_counters"]

    @admin.action(description="선택된 태그 카운터 초기화")
    def reset_counters(self, request, queryset):
        updated = 0
        for tag_counter in queryset:
            tag_counter.reset_all_counters()
            updated += 1
        self.message_user(request, f"{updated}개의 태그 카운터가 초기화되었습니다.")
