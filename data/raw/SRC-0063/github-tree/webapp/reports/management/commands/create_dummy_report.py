from django.core.management.base import BaseCommand
from django.db import transaction

from games.models import Game, GameResult, GameSession
from reports.choices import ReportStatusChoice
from reports.models import GameReport, GameReportAdvice, Report

from users.models import Child, User


class Command(BaseCommand):
    help = "Report 더미 데이터를 생성합니다 (User, Child, Game, GameSession, GameResult, GameReport, GameReportAdvice 포함)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default="dummy@example.com",
            help="생성할 사용자 이메일 (기본값: dummy@example.com)",
        )
        parser.add_argument(
            "--child-name",
            type=str,
            default="테스트아동",
            help="생성할 아동 이름 (기본값: 테스트아동)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        email = options["email"]
        child_name = options["child_name"]

        self.stdout.write(self.style.WARNING("더미 데이터 생성을 시작합니다..."))

        # 1. User 생성 또는 조회
        user, user_created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "is_active": True,
            },
        )
        if user_created:
            user.set_password("password123")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"✓ User 생성: {user.email}"))
        else:
            self.stdout.write(self.style.WARNING(f"○ User 이미 존재: {user.email}"))

        # 2. Child 생성 또는 조회
        child, child_created = Child.objects.get_or_create(
            parent=user,
            name=child_name,
            defaults={
                "birth_year": 2018,
                "gender": "M",
            },
        )
        if child_created:
            self.stdout.write(self.style.SUCCESS(f"✓ Child 생성: {child.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"○ Child 이미 존재: {child.name}"))

        # 3. Report 생성 또는 조회
        report, report_created = Report.objects.get_or_create(
            user=user,
            child=child,
            defaults={
                "concentration_score": 75,
                "status": ReportStatusChoice.COMPLETED,
            },
        )
        if report_created:
            self.stdout.write(self.style.SUCCESS(f"✓ Report 생성: {report}"))
        else:
            self.stdout.write(self.style.WARNING(f"○ Report 이미 존재: {report}"))

        # 4. 기존 Game 조회 (최대 2개)
        games = list(Game.objects.active()[:2])

        if not games:
            self.stdout.write(self.style.ERROR("✗ 사용 가능한 Game이 없습니다. 먼저 Game을 생성해주세요."))
            return

        self.stdout.write(self.style.SUCCESS(f"✓ 사용할 Game {len(games)}개 조회 완료"))
        for game in games:
            self.stdout.write(f"  - {game.name} ({game.code})")

        # 5. 각 게임에 대한 GameSession, GameResult, GameReport, GameReportAdvice 생성
        for idx, game in enumerate(games):
            # GameSession 생성 (매번 새로 생성)
            session = GameSession.objects.create(
                parent=user,
                child=child,
                game=game,
                status="COMPLETED",
                current_round=10,
                current_score=80 + (idx * 5),
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ GameSession 생성: {game.name} - Round {session.current_round}"))

            # GameResult 생성
            result = GameResult.objects.create(
                session=session,
                child=child,
                game=game,
                score=80 + (idx * 5),
                wrong_count=max(2 - idx, 0),
                success_count=8 + idx,
                round_count=10,
                reaction_ms_sum=5000 - (idx * 500),
                meta={
                    "difficulty": "normal",
                    "bonus_points": 10,
                },
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ GameResult 생성: {game.name} - Score: {result.score}"))

            # GameReport 생성
            game_report, game_report_created = GameReport.objects.get_or_create(
                report=report,
                game=game,
                defaults={
                    "last_reflected_session": session,
                    "meta": {
                        "average_score": result.score,
                        "total_sessions": 1,
                        "improvement_rate": 15.5,
                    },
                },
            )
            if game_report_created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ GameReport 생성: {game.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"  ○ GameReport 이미 존재: {game.name}"))

            # GameReportAdvice 생성 (각 게임당 2개)
            advices_data = [
                {
                    "title": f"{game.name} - 강점",
                    "description": f"아동은 {game.name}에서 우수한 성과를 보였습니다. 특히 집중력과 정확도가 뛰어났습니다.",
                },
                {
                    "title": f"{game.name} - 개선 제안",
                    "description": f"{game.name}의 반응 속도를 개선하기 위해 추가 연습이 필요합니다. 일주일에 2-3회 정도 연습을 권장합니다.",
                },
            ]

            for advice_data in advices_data:
                advice, advice_created = GameReportAdvice.objects.get_or_create(
                    game_report=game_report,
                    game=game,
                    title=advice_data["title"],
                    defaults={
                        "description": advice_data["description"],
                    },
                )
                if advice_created:
                    self.stdout.write(self.style.SUCCESS(f"    ✓ GameReportAdvice 생성: {advice.title}"))
                else:
                    self.stdout.write(self.style.WARNING(f"    ○ GameReportAdvice 이미 존재: {advice.title}"))

        # 최종 요약
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("더미 데이터 생성이 완료되었습니다!"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"User: {user.email}")
        self.stdout.write(f"Child: {child.name}")
        self.stdout.write(f"Report ID: {report.id}")
        self.stdout.write(f"GameReports: {report.game_reports.count()}개")
        self.stdout.write(f"GameReportAdvices: {sum(gr.advices.count() for gr in report.game_reports.all())}개")
        self.stdout.write("=" * 60)
