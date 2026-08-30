from django.contrib import admin
from tag.models import TagUserCounter


@admin.register(TagUserCounter)
class TagUserCounterAdmin(admin.ModelAdmin):
    list_display = (
        "tag",
        "user",
        "bookmarks_count",
        "bookmarkings_count",
        "created_at",
        "updated_at",
    )
    search_fields = ("tag__name", "user__email")
    list_filter = ("created_at", "updated_at")
    readonly_fields = (
        "bookmarks_count",
        "bookmarkings_count",
        "created_at",
        "updated_at",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("tag", "user")

    actions = ["reset_counters"]

    @admin.action(description="선택된 사용자 태그 카운터 초기화")
    def reset_counters(self, request, queryset):
        from tag.services.update_tag_counter_service import UpdateTagCounterService

        updated = 0
        for counter in queryset:
            result = UpdateTagCounterService(
                user=counter.user, tag=counter.tag
            ).update_counters()
            if result.get("updated"):
                updated += 1

        self.message_user(
            request, f"{updated}개의 사용자-태그 카운터가 초기화되었습니다."
        )
