from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from unfold.admin import ModelAdmin

from users.models import BotToken, User


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        "email",
        "username",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    search_fields = (
        "email",
        "username",
    )
    readonly_fields = (
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    fields = (
        "email",
        "username",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
        "updated_at",
    )

    actions = ("generate_bot_token",)

    @admin.action(description="선택한 사용자에 대한 BOT 토큰 생성")
    def generate_bot_token(self, request, queryset):
        """선택한 사용자에 대한 BOT 토큰을 생성합니다."""
        success_count = 0
        error_count = 0

        for user in queryset:
            try:
                bot_token = BotToken.create_for_report(user)
                success_count += 1

                # 생성된 토큰의 어드민 페이지 링크 표시
                token_admin_url = reverse("admin:users_bottoken_change", args=[bot_token.pk])
                messages.success(
                    request,
                    format_html(
                        "사용자 {} ({})의 BOT 토큰이 생성되었습니다. "
                        '<a href="{}" style="color: #2196F3; text-decoration: none; font-weight: 500;">토큰 보기 →</a>',
                        user.username,
                        user.email,
                        token_admin_url,
                    ),
                )
            except Exception as e:
                error_count += 1
                messages.error(
                    request,
                    f"사용자 {user.username}의 BOT 토큰 생성 중 오류 발생: {str(e)}",
                )

        # 요약 메시지
        if success_count > 0:
            self.message_user(
                request,
                f"{success_count}개의 BOT 토큰이 생성되었습니다.",
                messages.SUCCESS,
            )
        if error_count > 0:
            self.message_user(
                request,
                f"{error_count}개의 BOT 토큰 생성에 실패했습니다.",
                messages.ERROR,
            )
