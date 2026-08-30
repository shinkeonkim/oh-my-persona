from celery import shared_task
from django.contrib.auth import get_user_model
from meme.models import Meme
from tag.models import Tag, TagCounter
from tag.services.update_tag_counter_service import (
    UpdateAllTagCountersService,
    UpdateTagCounterService,
)


@shared_task
def update_tag_counter(tag_id):
    """
    태그 카운터 값을 업데이트하는 태스크

    Args:
        tag_id: 업데이트할 태그의 ID
    """
    try:
        tag = Tag.objects.get(id=tag_id)
        counter, _created = TagCounter.objects.get_or_create(tag=tag)
        counter.reset_all_counters()

        return f"{tag.name}#{tag_id} 의 카운터 업데이트 완료: 밈 {counter.memes_count}개, 북마킹 {counter.bookmarkings_count}회"
    except Tag.DoesNotExist:
        return f"태그 ID {tag_id}를 찾을 수 없음"
    except Exception as e:
        return f"오류 발생: {str(e)}"


@shared_task
def update_counter_for_user_and_tag(user_id, tag_id):
    """
    특정 사용자의 특정 태그에 대한 카운터를 업데이트하는 태스크

    Args:
        user_id: 업데이트할 사용자의 ID
        tag_id: 업데이트할 태그의 ID
    """
    try:
        result = UpdateTagCounterService(user=user_id, tag=tag_id).update_counters()

        if result.get("updated"):
            return (
                f"사용자 #{user_id}의 태그 #{tag_id} 카운터 업데이트 완료: "
                f"북마크 {result.get('bookmarks_count', 0)}, "
                f"북마킹 {result.get('bookmarkings_count', 0)}"
            )
        else:
            return f"사용자 #{user_id}는 태그 #{tag_id}에 대한 북마킹이 없습니다."
    except Exception as e:
        return f"오류 발생: {str(e)}"


@shared_task
def update_counters_for_user(user_id):
    """
    특정 사용자의 모든 태그 카운터를 업데이트하는 태스크

    Args:
        user_id: 업데이트할 사용자의 ID
    """
    try:
        result = UpdateTagCounterService(user=user_id).update_counters()

        return f"사용자 ID {user_id}의 모든 태그 카운터 업데이트 완료: {result.get('total_counters_updated', 0)}개 카운터 업데이트됨"
    except Exception as e:
        return f"오류 발생: {str(e)}"


@shared_task
def update_counters_for_tag(tag_id):
    """
    특정 태그와 관련된 모든 사용자의 카운터를 업데이트하는 태스크

    Args:
        tag_id: 업데이트할 태그의 ID
    """
    try:
        tag = Tag.objects.get(id=tag_id)

        try:
            counter = tag.tag_counter
        except TagCounter.DoesNotExist:
            counter = TagCounter.objects.create(tag=tag)

        counter.reset_all_counters()

        result = UpdateTagCounterService(tag=tag_id).update_counters()

        return (
            f"태그 ID {tag_id}({result.get('tag_name', '')})에 대한 모든 사용자 카운터 업데이트 완료: "
            f"{result.get('total_users_updated', 0)}명의 사용자 업데이트됨"
        )
    except Tag.DoesNotExist:
        return f"태그 ID {tag_id}를 찾을 수 없음"
    except Exception as e:
        return f"오류 발생: {str(e)}"


# 북마킹 관련 카운터 업데이트 태스크
@shared_task
def update_counters_for_bookmarking(user_id, meme_id):
    """
    북마킹에 관련된 모든 카운터(사용자 태그 카운터 및 태그 카운터)를 업데이트하는 태스크

    Args:
        user_id: 북마킹한 사용자의 ID
        meme_id: 북마킹된 밈의 ID
    """
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)
        meme = Meme.objects.get(id=meme_id)

        # Bookmark 모델의 bookmarkings_count 업데이트
        for bookmark in user.bookmarks.all():
            bookmark.reset_bookmarkings_count()

        # 북마킹된 밈에 연결된 태그 목록 가져오기
        tag_ids = meme.meme_taggings.filter(deleted_at__isnull=True).values_list(
            "tag_id", flat=True
        )

        # 사용자의 모든 태그 카운터 업데이트
        update_result = UpdateTagCounterService(user=user.id).update_counters()
        total_user_counters = update_result.get("total_counters_updated", 0)

        # 관련 태그들의 카운터 업데이트
        total_tags_updated = 0
        total_users_updated = 0
        for tag_id in tag_ids:
            # 태그 카운터 자체 업데이트
            tag = Tag.objects.get(id=tag_id)
            try:
                counter = tag.tag_counter
            except TagCounter.DoesNotExist:
                counter = TagCounter.objects.create(tag=tag)

            counter.reset_all_counters()

            # 태그에 대한 사용자 카운터 업데이트
            tag_result = UpdateTagCounterService(tag=tag_id).update_counters()
            total_tags_updated += 1
            total_users_updated += tag_result.get("total_users_updated", 0)

        return (
            f"북마킹 관련 카운터 업데이트 완료 - 사용자 ID: {user_id}, 밈 ID: {meme_id}, "
            f"업데이트된 사용자 태그 카운터: {total_user_counters}, "
            f"업데이트된 태그: {total_tags_updated}, 총 업데이트된 사용자-태그 관계: {total_users_updated}, "
            f"Bookmark 카운터 업데이트 완료"
        )
    except User.DoesNotExist:
        return f"사용자 ID {user_id}를 찾을 수 없음"
    except Meme.DoesNotExist:
        return f"밈 ID {meme_id}를 찾을 수 없음"
    except Exception as e:
        return f"오류 발생: {str(e)}"


# 전체 카운터 업데이트 태스크
@shared_task
def update_all_tag_counters():
    """
    모든 태그의 카운터를 업데이트하는 태스크

    각 태그에 대해 관련된 모든 사용자의 카운터 업데이트
    """
    try:
        # 모든 태그의 기본 카운터 업데이트
        tags = Tag.objects.filter(deleted_at__isnull=True)
        for tag in tags:
            try:
                counter = tag.tag_counter
            except TagCounter.DoesNotExist:
                counter = TagCounter.objects.create(tag=tag)

            counter.reset_all_counters()

        # 모든 태그 업데이트
        result = UpdateAllTagCountersService.update_all_tags()

        return (
            f"모든 태그 카운터 업데이트 완료: {result['total_tags_updated']}개 태그, "
            f"{result['total_users_updated']}개의 사용자-태그 관계 업데이트됨"
        )
    except Exception as e:
        return f"오류 발생: {str(e)}"


@shared_task
def update_all_user_counters():
    """
    모든 사용자의 태그 카운터를 비동기적으로 업데이트하는 Celery 태스크

    각 사용자에 대해 관련된 모든 태그 카운터 업데이트
    """
    try:
        # 모든 사용자 업데이트
        result = UpdateAllTagCountersService.update_all_users()

        return (
            f"모든 사용자의 태그 카운터 업데이트 완료: "
            f"{result['total_users_updated']}명의 사용자, "
            f"{result['total_counters_updated']}개의 카운터 업데이트됨"
        )
    except Exception as e:
        return f"오류 발생: {str(e)}"
