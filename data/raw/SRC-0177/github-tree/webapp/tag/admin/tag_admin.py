from django.contrib import admin
from tag.models import Tag, TagCounter, TagUserCounter
from unfold.admin import ModelAdmin


class TagCounterInline(admin.StackedInline):
    model = TagCounter
    can_delete = False
    readonly_fields = ("memes_count", "bookmarkings_count", "created_at", "updated_at")
    max_num = 1
    min_num = 1
    extra = 0
    verbose_name = "태그 카운터"
    verbose_name_plural = "태그 카운터"

    def has_add_permission(self, request, obj):
        # 이미 있으면 추가 불가능
        if obj and hasattr(obj, "tag_counter"):
            return False
        return True


class TagUserCounterInline(admin.TabularInline):
    model = TagUserCounter
    can_delete = False
    readonly_fields = (
        "user",
        "bookmarks_count",
        "bookmarkings_count",
        "created_at",
        "updated_at",
    )
    max_num = 0  # 보기만 가능
    extra = 0
    verbose_name = "사용자 태그 카운터"
    verbose_name_plural = "사용자 태그 카운터 목록"

    def has_add_permission(self, request, obj):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = (
        "name",
        "get_memes_count",
        "get_bookmarkings_count",
        "get_user_count",
        "created_at",
        "updated_at",
    )
    list_filter = ("name", "category")
    search_fields = ("name",)
    ordering = ("-created_at",)

    exclude = ["deleted_at"]
    readonly_fields = [
        "split_name",
        "first_letter",
        "created_at",
        "updated_at",
        "deleted_at",
    ]

    fields = (
        "name",
        "split_name",
        "first_letter",
        "description",
        "category",
        "created_at",
        "updated_at",
    )

    inlines = [TagCounterInline, TagUserCounterInline]

    def get_memes_count(self, obj):
        if hasattr(obj, "tag_counter"):
            return obj.tag_counter.memes_count
        return 0

    get_memes_count.short_description = "밈 수"

    def get_bookmarkings_count(self, obj):
        if hasattr(obj, "tag_counter"):
            return obj.tag_counter.bookmarkings_count
        return 0

    get_bookmarkings_count.short_description = "북마킹 수"

    def get_user_count(self, obj):
        return obj.user_tag_counters.count()

    get_user_count.short_description = "사용자 수"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("tag_counter", "user_tag_counters")
        )

    actions = ["reset_tag_counters", "reset_user_tag_counters"]

    @admin.action(description="선택된 태그의 카운터 초기화")
    def reset_tag_counters(self, request, queryset):
        updated = 0
        for tag in queryset:
            if hasattr(tag, "tag_counter"):
                # 태그 카운터 업데이트 - 기존 모델 메서드 사용 (성능 최적화되어 있음)
                tag.tag_counter.reset_all_counters()
                updated += 1
            else:
                # 태그 카운터가 없는 경우 생성
                counter = TagCounter.objects.create(tag=tag)
                counter.reset_all_counters()
                updated += 1
        self.message_user(request, f"{updated}개의 태그 카운터가 초기화되었습니다.")

    @admin.action(description="선택된 태그의 사용자 카운터 초기화")
    def reset_user_tag_counters(self, request, queryset):
        from tag.services.update_tag_counter_service import UpdateTagCounterService

        updated_tags = 0
        updated_users = 0

        for tag in queryset:
            result = UpdateTagCounterService(tag=tag).update_counters()
            updated_tags += 1
            updated_users += result["total_users_updated"]

        self.message_user(
            request,
            f"{updated_tags}개 태그에 대해 총 {updated_users}명의 사용자 카운터가 초기화되었습니다.",
        )
