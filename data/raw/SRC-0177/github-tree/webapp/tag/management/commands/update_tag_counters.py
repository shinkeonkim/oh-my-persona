from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from tag.models import Tag
from tag.services.update_tag_counter_service import (
    UpdateAllTagCountersService,
    UpdateTagCounterService,
)

User = get_user_model()


class Command(BaseCommand):
    help = "태그 카운터를 업데이트합니다 (사용자의 태그 카운터 또는 태그에 대한 사용자 카운터)"

    def add_arguments(self, parser):
        # 태그 관련 인자
        tag_group = parser.add_argument_group("태그 옵션")
        tag_group.add_argument(
            "--tag-id",
            type=int,
            help="특정 태그의 ID",
        )

        # 사용자 관련 인자
        user_group = parser.add_argument_group("사용자 옵션")
        user_group.add_argument(
            "--user-id",
            type=int,
            help="특정 사용자의 ID",
        )

        # 공통 옵션
        parser.add_argument(
            "--async",
            action="store_true",
            help="비동기 처리 활성화 (Celery 태스크 사용)",
        )

        parser.add_argument(
            "--quiet",
            action="store_true",
            help="진행 상황 메시지 숨김",
        )

    def handle(self, *args, **options):
        tag_id = options.get("tag_id")
        user_id = options.get("user_id")
        use_async = options.get("async")
        quiet = options.get("quiet")

        # 사용자와 태그 식별자 확인
        user = None
        tag = None

        # 사용자 지정 확인
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                if not quiet:
                    self.stdout.write(f"사용자 ID: {user_id}를 찾았습니다.")
            except User.DoesNotExist:
                raise CommandError(f"사용자 ID: {user_id}를 찾을 수 없습니다.")

        # 태그 지정 확인
        if tag_id:
            try:
                tag = Tag.objects.get(id=tag_id)
                if not quiet:
                    self.stdout.write(f"태그 ID: {tag_id} ({tag.name})를 찾았습니다.")
            except Tag.DoesNotExist:
                raise CommandError(f"태그 ID: {tag_id}를 찾을 수 없습니다.")

        # 경우에 따른 처리
        if tag_id or user_id:
            if use_async:
                self._handle_async(user, tag, quiet)
            else:
                self._handle_sync(user, tag, quiet)
        else:
            # 모든 태그와 사용자에 대한 업데이트
            if not quiet:
                self.stdout.write(
                    self.style.NOTICE("모든 태그와 사용자에 대한 카운터 업데이트 중...")
                )

            if use_async:
                self._handle_all_async(quiet)
            else:
                self._handle_all_sync(quiet)

    def _handle_sync(self, user, tag, quiet):
        """동기적으로 카운터 업데이트 (개별 태그/사용자)"""
        service = UpdateTagCounterService(user=user, tag=tag)

        try:
            if user and tag:
                if not quiet:
                    self.stdout.write(
                        self.style.NOTICE(
                            f"사용자 '{user.email}'의 태그 '{tag.name}' 카운터 업데이트 중..."
                        )
                    )
            elif user:
                if not quiet:
                    self.stdout.write(
                        self.style.NOTICE(
                            f"사용자 '{user.email}'의 모든 태그 카운터 업데이트 중..."
                        )
                    )
            elif tag:
                if not quiet:
                    self.stdout.write(
                        self.style.NOTICE(
                            f"태그 '{tag.name}'에 대한 모든 사용자 카운터 업데이트 중..."
                        )
                    )

            result = service.update_counters()

            # 결과 출력
            if user and tag:
                if result.get("updated"):
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"완료! 사용자 '{user.email}'의 태그 '{tag.name}' 카운터 업데이트됨: "
                            f"북마크 {result.get('bookmarks_count', 0)}, 북마킹 {result.get('bookmarkings_count', 0)}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"사용자 '{user.email}'는 태그 '{tag.name}'에 대한 북마킹이 없습니다."
                        )
                    )
            elif user:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"완료! 사용자 '{user.email}'의 {result.get('total_counters_updated', 0)}개 태그 카운터가 업데이트되었습니다."
                    )
                )
            elif tag:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"완료! 태그 '{tag.name}'에 대해 {result.get('total_users_updated', 0)}명의 사용자 카운터가 업데이트되었습니다."
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"에러 발생: {str(e)}"))

    def _handle_async(self, user, tag, quiet):
        """비동기적으로 카운터 업데이트 (개별 태그/사용자)"""
        if user and tag:
            from tag.tasks.tag_counter_tasks import update_counter_for_user_and_tag

            task = update_counter_for_user_and_tag.delay(user.id, tag.id)
            self.stdout.write(
                self.style.SUCCESS(
                    f"사용자 '{user.email}'의 태그 '{tag.name}' 카운터 업데이트 비동기 태스크 시작됨! (Task ID: {task.id})"
                )
            )

        elif user:
            from tag.tasks.tag_counter_tasks import update_counters_for_user

            task = update_counters_for_user.delay(user.id)
            self.stdout.write(
                self.style.SUCCESS(
                    f"사용자 '{user.email}'의 모든 태그 카운터 업데이트 비동기 태스크 시작됨! (Task ID: {task.id})"
                )
            )

        elif tag:
            from tag.tasks.tag_counter_tasks import update_counters_for_tag

            task = update_counters_for_tag.delay(tag.id)
            self.stdout.write(
                self.style.SUCCESS(
                    f"태그 '{tag.name}'에 대한 모든 사용자 카운터 업데이트 비동기 태스크 시작됨! (Task ID: {task.id})"
                )
            )

    def _handle_all_sync(self, quiet):
        """동기적으로 모든 태그/사용자 카운터 업데이트"""
        # 모든 태그 업데이트
        if not quiet:
            self.stdout.write(
                self.style.NOTICE("모든 태그에 대한 사용자 카운터 업데이트 중...")
            )

        tag_result = UpdateAllTagCountersService.update_all_tags()

        # 모든 사용자 업데이트
        if not quiet:
            self.stdout.write(
                self.style.NOTICE("모든 사용자의 태그 카운터 업데이트 중...")
            )

        user_result = UpdateAllTagCountersService.update_all_users()

        self.stdout.write(
            self.style.SUCCESS(
                f"완료! {tag_result['total_tags_updated']}개 태그와 "
                f"{user_result['total_users_updated']}명의 사용자 카운터가 업데이트되었습니다. "
                f"총 {tag_result['total_users_updated']}개의 사용자-태그 관계가 업데이트됨."
            )
        )

    def _handle_all_async(self, quiet):
        """비동기적으로 모든 태그/사용자 카운터 업데이트"""
        from tag.tasks.tag_counter_tasks import (
            update_all_tag_counters,
            update_all_user_counters,
        )

        # 모든 태그 비동기 업데이트
        task1 = update_all_tag_counters.delay()
        self.stdout.write(
            self.style.SUCCESS(
                f"모든 태그에 대한 비동기 태스크 시작됨! (Task ID: {task1.id})"
            )
        )

        # 모든 사용자 비동기 업데이트
        task2 = update_all_user_counters.delay()
        self.stdout.write(
            self.style.SUCCESS(
                f"모든 사용자에 대한 비동기 태스크 시작됨! (Task ID: {task2.id})"
            )
        )
