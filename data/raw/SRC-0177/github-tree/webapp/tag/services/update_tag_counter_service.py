from django.contrib.auth import get_user_model
from django.db import transaction
from tag.models import Tag, TagUserCounter

User = get_user_model()


class UpdateTagCounterService:
    """
    태그 카운터 업데이트를 위한 통합 서비스

    다음 세 가지 시나리오를 지원:
    1. 특정 사용자의 모든 태그 카운터 업데이트
    2. 특정 태그의 모든 사용자 카운터 업데이트
    3. 특정 사용자의 특정 태그에 대한 카운터 업데이트
    """

    def __init__(self, user=None, tag=None):
        """
        Args:
            user: 사용자 객체 또는 사용자 ID (옵션)
            tag: 태그 객체 또는 태그 ID (옵션)
        """
        self._user = None
        self.user_id = None
        if user is not None:
            if isinstance(user, int):
                self.user_id = user
            else:
                self.user_id = user.id
                self._user = user

        self._tag = None
        self.tag_id = None
        if tag is not None:
            if isinstance(tag, int):
                self.tag_id = tag
            else:
                self.tag_id = tag.id
                self._tag = tag

    @property
    def user(self):
        if self._user is None and self.user_id is not None:
            self._user = User.objects.get(id=self.user_id)
        return self._user

    @property
    def tag(self):
        if self._tag is None and self.tag_id is not None:
            self._tag = Tag.objects.get(id=self.tag_id)
        return self._tag

    @transaction.atomic
    def update_counters(self):
        """
        상황에 따라 적절한 카운터 업데이트 수행

        Returns:
            dict: 업데이트 결과 정보
        """
        if self.user_id is not None and self.tag_id is not None:
            return self._update_counter_for_user_and_tag()
        elif self.user_id is not None:
            return self._update_counters_for_user()
        elif self.tag_id is not None:
            return self._update_counters_for_tag()
        else:
            # 인자가 제공되지 않음
            raise ValueError("사용자 또는 태그를 지정해야 합니다.")

    def _update_counter_for_user_and_tag(self):
        """특정 사용자의 특정 태그에 대한 카운터 업데이트"""
        counter = TagUserCounter.reset_counter_for_tag(self.user, self.tag)

        result = {
            "user_id": self.user_id,
            "tag_id": self.tag_id,
            "tag_name": self.tag.name if self.tag else None,
            "updated": counter is not None,
        }

        if counter:
            result.update(
                {
                    "bookmarks_count": counter.bookmarks_count,
                    "bookmarkings_count": counter.bookmarkings_count,
                }
            )

        return result

    def _update_counters_for_user(self):
        """특정 사용자의 모든 태그 카운터 업데이트"""
        TagUserCounter.reset_all_counters(self.user)

        # 업데이트된 카운터 수 계산
        updated_count = TagUserCounter.objects.filter(user=self.user).count()

        return {"user_id": self.user_id, "total_counters_updated": updated_count}

    def _update_counters_for_tag(self):
        """특정 태그와 관련된 모든 사용자 카운터 업데이트"""
        # 태그가 적용된 밈을 북마크한 모든 유저 찾기
        query = """
            SELECT DISTINCT u.id
            FROM {user_table} u
            JOIN bookmarkings ON bookmarkings.user_id = u.id
            JOIN memes ON bookmarkings.meme_id = memes.id
            JOIN meme_taggings ON meme_taggings.meme_id = memes.id
            WHERE meme_taggings.tag_id = %s AND meme_taggings.deleted_at IS NULL
        """

        user_ids = User.objects.raw(
            query.format(user_table=User._meta.db_table), [self.tag_id]
        )

        # ID 목록 추출
        user_id_list = [user.id for user in user_ids]
        total_users = len(user_id_list)

        # 배치 처리
        batch_size = 100
        processed_users = 0

        for i in range(0, total_users, batch_size):
            batch_ids = user_id_list[i : i + batch_size]

            users = User.objects.filter(id__in=batch_ids)
            for user in users:
                TagUserCounter.reset_counter_for_tag(user, self.tag)
                processed_users += 1

        return {
            "tag_id": self.tag_id,
            "tag_name": self.tag.name,
            "total_users_updated": processed_users,
        }


class UpdateAllTagCountersService:
    """
    모든 태그 또는 사용자의 카운터를 업데이트하는 서비스
    """

    @staticmethod
    @transaction.atomic
    def update_all_tags():
        """모든 태그에 대한 카운터 업데이트"""
        tags = Tag.objects.filter(deleted_at__isnull=True)
        tag_count = tags.count()

        total_users_updated = 0

        for tag in tags:
            result = UpdateTagCounterService(tag=tag).update_counters()
            total_users_updated += result["total_users_updated"]

        return {
            "total_tags_updated": tag_count,
            "total_users_updated": total_users_updated,
        }

    @staticmethod
    @transaction.atomic
    def update_all_users():
        """모든 사용자의 카운터 업데이트"""
        users = User.objects.all()
        user_count = users.count()

        total_counters_updated = 0

        for user in users:
            result = UpdateTagCounterService(user=user).update_counters()
            total_counters_updated += result["total_counters_updated"]

        return {
            "total_users_updated": user_count,
            "total_counters_updated": total_counters_updated,
        }
