from django.contrib import admin, messages
from django.db.models import F, Max, Q, Window
from django.db.models.functions import Rank
from django.utils.html import format_html

from games.choices import GameCodeChoice
from games.models import RankingEntry
from unfold.admin import ModelAdmin


@admin.register(RankingEntry)
class RankingEntryAdmin(ModelAdmin):
    """랭킹 엔트리 관리자 페이지"""

    list_display = (
        "rank_display",
        "player_name",
        "organization",
        "game_info",
        "score_display",
        "round_count",
        "event_highlight",
        "contact_info",
        "created_at",
    )
    list_filter = (
        "game",
        "is_event_highlighted",
        "created_at",
    )
    search_fields = (
        "player_name",
        "organization",
        "game__name",
        "game__code",
        "contact_info",
    )
    ordering = ("-score", "-round_count", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = (
        "game",
        "score",
        "round_count",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("game_result",)

    fieldsets = (
        (
            "게임 결과 선택",
            {
                "fields": ("game_result",),
                "description": "랭킹에 등록할 게임 결과를 선택하세요. 선택하면 게임, 점수, 라운드가 자동으로 채워집니다.",
            },
        ),
        (
            "참가자 정보",
            {
                "fields": (
                    "player_name",
                    "organization",
                    "contact_info",
                ),
                "description": "데모부스에서 참가자가 입력한 이름, 소속, 연락처를 입력하세요.",
            },
        ),
        (
            "게임 정보 (자동 채움)",
            {
                "fields": (
                    "game",
                    "score",
                    "round_count",
                ),
                "description": "게임 결과를 선택하면 자동으로 채워집니다.",
                "classes": ("collapse",),
            },
        ),
        (
            "이벤트 설정",
            {
                "fields": (
                    "is_event_highlighted",
                    "event_triggered_at",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "시스템 정보",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    list_per_page = 25
    show_full_result_count = True

    actions = ["clear_event_highlights", "reset_rankings"]

    def rank_display(self, obj):
        """랭킹 순위 표시 (게임별로 계산) - Window function으로 미리 계산된 rank 사용"""
        # Window function으로 미리 계산된 rank 사용
        rank = getattr(obj, "rank", None)
        if rank is None:
            # fallback: annotation이 없는 경우 기존 방식 사용
            queryset = self.get_queryset(None).filter(game=obj.game) if obj.game else self.get_queryset(None)
            rank = (
                queryset.filter(
                    Q(score__gt=obj.score)
                    | Q(score=obj.score, round_count__gt=obj.round_count)
                    | Q(
                        score=obj.score,
                        round_count=obj.round_count,
                        created_at__lt=obj.created_at,
                    )
                ).count()
                + 1
            )

        if rank == 1:
            return format_html(
                '<span style="font-weight: bold; color: #FFD700; font-size: 1.2em;">🥇 {}</span>',
                rank,
            )
        elif rank == 2:
            return format_html(
                '<span style="font-weight: bold; color: #C0C0C0; font-size: 1.1em;">🥈 {}</span>',
                rank,
            )
        elif rank == 3:
            return format_html(
                '<span style="font-weight: bold; color: #CD7F32; font-size: 1.1em;">🥉 {}</span>',
                rank,
            )
        else:
            return format_html("<span>{}</span>", rank)

    rank_display.short_description = "순위"

    def game_info(self, obj):
        """게임 정보 표시"""
        if obj.game:
            return format_html(
                "<strong>{}</strong><br/><small>{}</small>",
                obj.game.name,
                obj.game.code,
            )
        return "-"

    game_info.short_description = "게임"
    game_info.admin_order_field = "game__name"

    def score_display(self, obj):
        """점수 표시 (색상 포함) - Window function으로 미리 계산된 top_score 사용"""
        # Window function으로 미리 계산된 top_score_in_game 사용
        top_score = getattr(obj, "top_score_in_game", None)
        if top_score is None:
            # fallback: annotation이 없는 경우 기존 방식 사용
            top_score = RankingEntry.objects.get_top_score(obj.game) if obj.game else 0

        if obj.score == top_score and obj.score > 0:
            return format_html(
                '<strong style="color: #FFD700; font-size: 1.2em;">⭐ {}</strong>',
                obj.score,
            )
        elif obj.score >= 80:
            color = "#4CAF50"  # Green
        elif obj.score >= 60:
            color = "#FF9800"  # Orange
        else:
            color = "#F44336"  # Red

        return format_html(
            '<strong style="color: {}; font-size: 1.1em;">{}</strong>',
            color,
            obj.score,
        )

    score_display.short_description = "점수"
    score_display.admin_order_field = "score"

    def event_highlight(self, obj):
        """이벤트 하이라이트 표시"""
        if obj.is_event_highlighted:
            return format_html(
                '<span style="background-color: #FFD700; color: #000; padding: 4px 8px; border-radius: 4px; font-weight: bold;">🎉 최고점!</span>'
            )
        return "-"

    event_highlight.short_description = "이벤트"
    event_highlight.boolean = True

    def contact_info(self, obj):
        """연락처 표시"""
        return obj.contact_info or "-"

    contact_info.short_description = "연락처"

    def get_queryset(self, request):
        """쿼리셋 최적화 - Window function으로 rank와 top_score 미리 계산"""
        queryset = super().get_queryset(request)
        return queryset.select_related("game", "game_result").annotate(
            rank=Window(
                expression=Rank(),
                partition_by=[F("game_id")],
                order_by=[
                    F("score").desc(),
                    F("round_count").desc(),
                    F("created_at").asc(),
                ],
            ),
            top_score_in_game=Window(
                expression=Max("score"),
                partition_by=[F("game_id")],
            ),
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """GameResult 및 Game 선택 시 아기별 게임과 교통 게임 필터링"""
        if db_field.name == "game_result":
            # 아기별 게임과 교통 게임의 결과만 필터링
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                game__code__in=[GameCodeChoice.BB_STAR, GameCodeChoice.KIDS_TRAFFIC]
            ).select_related("game", "child")
        elif db_field.name == "game":
            # 아기별 게임과 교통 게임만 선택 가능
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                code__in=[GameCodeChoice.BB_STAR, GameCodeChoice.KIDS_TRAFFIC]
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.action(description="선택한 항목의 이벤트 하이라이트 해제")
    def clear_event_highlights(self, request, queryset):
        """선택한 항목의 이벤트 하이라이트 해제"""
        updated = queryset.update(is_event_highlighted=False, event_triggered_at=None)
        self.message_user(
            request,
            f"{updated}개의 항목에서 이벤트 하이라이트를 해제했습니다.",
            messages.SUCCESS,
        )

    @admin.action(description="선택한 게임의 랭킹 초기화 (주의: 삭제됩니다)")
    def reset_rankings(self, request, queryset):
        """선택한 게임의 랭킹 초기화"""
        if queryset.count() == 0:
            self.message_user(request, "선택한 항목이 없습니다.", messages.WARNING)
            return

        # 게임별로 그룹화
        games = set(queryset.values_list("game", flat=True))
        game_names = [obj.game.name for obj in queryset.select_related("game")[:1]]

        deleted_count, _ = queryset.delete()

        self.message_user(
            request,
            f"{deleted_count}개의 랭킹 항목을 삭제했습니다. (게임: {', '.join(set(game_names))})",
            messages.SUCCESS,
        )

    def save_model(self, request, obj, form, change):
        """모델 저장 시 GameResult에서 정보 자동 채우기 및 최고점 체크"""
        # game_result가 선택되었으면 자동으로 game, score, round_count 채우기
        if obj.game_result:
            obj.game = obj.game_result.game
            obj.score = obj.game_result.score
            obj.round_count = obj.game_result.round_count

        super().save_model(request, obj, form, change)

        # 저장 후 최고점 갱신 체크
        if obj.game and obj.score > 0:
            # 현재 게임의 최고점 조회 (자기 자신 포함)
            top_entry = (
                RankingEntry.objects.filter(game=obj.game).order_by("-score", "-round_count", "created_at").first()
            )

            # 자신이 최고점이면 하이라이트 설정
            if top_entry and top_entry.id == obj.id:
                # 기존 최고점의 하이라이트 해제 (자기 자신 제외)
                RankingEntry.objects.filter(
                    game=obj.game,
                    is_event_highlighted=True,
                ).exclude(id=obj.id).update(
                    is_event_highlighted=False,
                    event_triggered_at=None,
                )
                # 새 최고점 하이라이트 설정 (아직 설정되지 않았다면)
                if not obj.is_event_highlighted:
                    obj.is_event_highlighted = True
                    from django.utils import timezone

                    obj.event_triggered_at = timezone.now()
                    obj.save(update_fields=["is_event_highlighted", "event_triggered_at"])
