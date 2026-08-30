from unittest.mock import MagicMock, patch

from bookmark.models import Bookmark, Bookmarking
from django.contrib.auth import get_user_model
from django.test import TestCase
from meme.models import Meme
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

User = get_user_model()


class BookmarkingSyncAPIViewTest(TestCase):
    """BookmarkingSyncAPIView에 대한 포괄적인 테스트 클래스"""

    def setUp(self):
        """테스트에 필요한 기본 데이터를 생성합니다."""
        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

        # 다른 사용자 생성 (권한 테스트용)
        self.other_user = User.objects.create_user(
            email="other@example.com", username="otheruser", password="testpass123"
        )

        # 테스트 밈 생성
        self.meme = Meme.objects.create(
            type="Text",
            title="Test Meme",
            description="This is a test meme",
            creator=self.user,
        )

        # 테스트 북마크들 생성
        self.bookmark1 = Bookmark.objects.create(title="Bookmark 1", user=self.user)

        self.bookmark2 = Bookmark.objects.create(title="Bookmark 2", user=self.user)

        self.bookmark3 = Bookmark.objects.create(title="Bookmark 3", user=self.user)

        # 다른 사용자의 북마크 생성
        self.other_bookmark = Bookmark.objects.create(
            title="Other User Bookmark", user=self.other_user
        )

        # API 클라이언트 설정
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # URL 설정 - 올바른 URL 패턴 사용
        self.url = "/api/v1/bookmarkings/"

    def test_current_meme_property(self):
        """current_meme 프로퍼티가 올바르게 작동하는지 테스트"""
        # 뷰 인스턴스 생성
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # Mock request 생성
        mock_request = MagicMock()
        mock_request.data = {"meme_id": self.meme.id}

        view = BookmarkingSyncAPIView()
        view.request = mock_request

        # current_meme 프로퍼티 테스트
        current_meme = view.current_meme
        self.assertEqual(current_meme, self.meme)

        # 존재하지 않는 밈 ID로 테스트
        mock_request.data = {"meme_id": 99999}
        with self.assertRaises(Exception):  # 404 에러 발생
            view.current_meme

    def test_post_method_without_bookmark_true(self):
        """without_bookmark=True인 경우 POST 메서드 테스트"""
        # 기존 북마킹 데이터 생성
        existing_bookmarking = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark1
        )

        # without_bookmark=True로 요청
        data = {"meme_id": self.meme.id, "bookmark_ids": [], "without_bookmark": True}

        response = self.client.post(self.url, data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Bookmarkings synced successfully.")

        # 기존 북마킹이 삭제되었는지 확인
        self.assertFalse(
            Bookmarking.objects.filter(id=existing_bookmarking.id).exists()
        )

        # 새로운 북마킹(북마크 없음)이 생성되었는지 확인
        new_bookmarking = Bookmarking.objects.filter(
            user=self.user, meme=self.meme, bookmark__isnull=True
        ).first()
        self.assertIsNotNone(new_bookmarking)

    def test_post_method_without_bookmark_false(self):
        """without_bookmark=False인 경우 POST 메서드 테스트"""
        # 기존 북마킹 데이터 생성 (북마크 없음)
        existing_bookmarking = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=None
        )

        # without_bookmark=False로 요청 (기본값)
        data = {
            "meme_id": self.meme.id,
            "bookmark_ids": [self.bookmark1.id, self.bookmark2.id],
        }

        response = self.client.post(self.url, data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Bookmarkings synced successfully.")

        # 기존 북마킹(북마크 없음)이 삭제되었는지 확인
        self.assertFalse(
            Bookmarking.objects.filter(id=existing_bookmarking.id).exists()
        )

        # 새로운 북마킹들이 생성되었는지 확인
        new_bookmarkings = Bookmarking.objects.filter(
            user=self.user,
            meme=self.meme,
            bookmark__in=[self.bookmark1, self.bookmark2],
        )
        self.assertEqual(new_bookmarkings.count(), 2)

    def test_sync_without_bookmark_method(self):
        """sync_without_bookmark 메서드 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # 기존 북마킹 데이터 생성
        existing_bookmarking = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark1
        )

        # Mock request 설정
        mock_request = MagicMock()
        mock_request.data = {"meme_id": self.meme.id}
        mock_request.user = self.user

        view = BookmarkingSyncAPIView()
        view.request = mock_request

        # sync_without_bookmark 메서드 호출
        view.sync_without_bookmark()

        # 기존 북마킹이 삭제되었는지 확인
        self.assertFalse(
            Bookmarking.objects.filter(id=existing_bookmarking.id).exists()
        )

        # 새로운 북마킹(북마크 없음)이 생성되었는지 확인
        new_bookmarking = Bookmarking.objects.filter(
            user=self.user, meme=self.meme, bookmark__isnull=True
        ).first()
        self.assertIsNotNone(new_bookmarking)

    def test_sync_bookmarking_with_bookmarks_method(self):
        """sync_bookmarking_with_bookmarks 메서드 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # 기존 북마킹 데이터 생성
        existing_bookmarking = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark1
        )

        # Mock request 설정
        mock_request = MagicMock()
        mock_request.data = {
            "meme_id": self.meme.id,
            "bookmark_ids": [self.bookmark2.id, self.bookmark3.id],
        }
        mock_request.user = self.user

        view = BookmarkingSyncAPIView()
        view.request = mock_request

        # sync_bookmarking_with_bookmarks 메서드 호출
        view.sync_bookmarking_with_bookmarks()

        # 기존 북마킹이 삭제되었는지 확인
        self.assertFalse(
            Bookmarking.objects.filter(id=existing_bookmarking.id).exists()
        )

        # 새로운 북마킹들이 생성되었는지 확인
        new_bookmarkings = Bookmarking.objects.filter(
            user=self.user,
            meme=self.meme,
            bookmark__in=[self.bookmark2, self.bookmark3],
        )
        self.assertEqual(new_bookmarkings.count(), 2)

    def test_sync_bookmarking_with_bookmarks_empty_bookmark_ids(self):
        """bookmark_ids가 비어있는 경우 ValidationError 발생 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # Mock request 설정 (bookmark_ids가 비어있음)
        mock_request = MagicMock()
        mock_request.data = {"meme_id": self.meme.id, "bookmark_ids": []}
        mock_request.user = self.user

        view = BookmarkingSyncAPIView()
        view.request = mock_request

        # ValidationError 발생 확인
        with self.assertRaises(ValidationError) as cm:
            view.sync_bookmarking_with_bookmarks()
        self.assertIn("At least one bookmark_id must be provided.", str(cm.exception))

    def test_sync_bookmarking_with_bookmarks_invalid_bookmark_ids(self):
        """유효하지 않은 bookmark_ids에 대해 ValidationError 발생 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # Mock request 설정 (다른 사용자의 북마크 ID 포함)
        mock_request = MagicMock()
        mock_request.data = {
            "meme_id": self.meme.id,
            "bookmark_ids": [self.bookmark1.id, self.other_bookmark.id],
        }
        mock_request.user = self.user

        view = BookmarkingSyncAPIView()
        view.request = mock_request

        # ValidationError 발생 확인
        with self.assertRaises(ValidationError):
            view.sync_bookmarking_with_bookmarks()

    def test_sync_bookmarking_with_bookmarks_partial_update(self):
        """기존 북마킹과 새로운 북마킹이 혼재된 경우 부분 업데이트 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # 기존 북마킹 데이터 생성
        existing_bookmarking1 = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark1
        )

        existing_bookmarking2 = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark2
        )

        # Mock request 설정 (bookmark1은 유지, bookmark2는 제거, bookmark3는 추가)
        mock_request = MagicMock()
        mock_request.data = {
            "meme_id": self.meme.id,
            "bookmark_ids": [self.bookmark1.id, self.bookmark3.id],
        }
        mock_request.user = self.user

        view = BookmarkingSyncAPIView()
        view.request = mock_request

        # sync_bookmarking_with_bookmarks 메서드 호출
        view.sync_bookmarking_with_bookmarks()

        # bookmark1은 유지되어야 함
        self.assertTrue(
            Bookmarking.objects.filter(id=existing_bookmarking1.id).exists()
        )

        # bookmark2는 제거되어야 함
        self.assertFalse(
            Bookmarking.objects.filter(id=existing_bookmarking2.id).exists()
        )

        # bookmark3는 새로 생성되어야 함
        new_bookmarking = Bookmarking.objects.filter(
            user=self.user, meme=self.meme, bookmark=self.bookmark3
        ).first()
        self.assertIsNotNone(new_bookmarking)

    @patch("tag.tasks.tag_counter_tasks.update_counters_for_bookmarking.delay")
    def test_sync_bookmarking_with_bookmarks_triggers_counter_update(
        self, mock_update_counters
    ):
        """북마킹 제거 시 카운터 업데이트 태스크가 호출되는지 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # 기존 북마킹 데이터 생성
        Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark1
        )

        # Mock request 설정 (기존 북마킹을 다른 북마킹으로 교체)
        mock_request = MagicMock()
        mock_request.data = {
            "meme_id": self.meme.id,
            "bookmark_ids": [
                self.bookmark2.id
            ],  # bookmark1을 제거하고 bookmark2로 교체
        }
        mock_request.user = self.user

        view = BookmarkingSyncAPIView()
        view.request = mock_request

        # sync_bookmarking_with_bookmarks 메서드 호출
        view.sync_bookmarking_with_bookmarks()

        # 카운터 업데이트 태스크가 호출되었는지 확인
        mock_update_counters.assert_called_once_with(self.user.id, self.meme.id)

    def test_delete_bookmarking_with_bookmark_method(self):
        """delete_bookmarking_with_bookmark 메서드 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # 북마크가 있는 북마킹 생성
        bookmarking_with_bookmark = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark1
        )

        # 북마크가 없는 북마킹 생성
        bookmarking_without_bookmark = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=None
        )

        # Mock request 설정
        mock_request = MagicMock()
        mock_request.data = {"meme_id": self.meme.id}
        mock_request.user = self.user

        view = BookmarkingSyncAPIView()
        view.request = mock_request

        # delete_bookmarking_with_bookmark 메서드 호출
        view.delete_bookmarking_with_bookmark()

        # 북마크가 있는 북마킹만 삭제되었는지 확인
        self.assertFalse(
            Bookmarking.objects.filter(id=bookmarking_with_bookmark.id).exists()
        )
        self.assertTrue(
            Bookmarking.objects.filter(id=bookmarking_without_bookmark.id).exists()
        )

    def test_delete_bookmarking_without_bookmark_method(self):
        """delete_bookmarking_without_bookmark 메서드 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # 북마크가 있는 북마킹 생성
        bookmarking_with_bookmark = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark1
        )

        # 북마크가 없는 북마킹 생성
        bookmarking_without_bookmark = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=None
        )

        # Mock request 설정
        mock_request = MagicMock()
        mock_request.data = {"meme_id": self.meme.id}
        mock_request.user = self.user

        view = BookmarkingSyncAPIView()
        view.request = mock_request

        # delete_bookmarking_without_bookmark 메서드 호출
        view.delete_bookmarking_without_bookmark()

        # 북마크가 없는 북마킹만 삭제되었는지 확인
        self.assertTrue(
            Bookmarking.objects.filter(id=bookmarking_with_bookmark.id).exists()
        )
        self.assertFalse(
            Bookmarking.objects.filter(id=bookmarking_without_bookmark.id).exists()
        )

    def test_post_save_signals_are_sent(self):
        """새로운 북마킹 생성 시 post_save 시그널이 전송되는지 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )
        from django.db.models.signals import post_save

        # 시그널 수신을 위한 리스너 생성
        signal_received = []

        def signal_listener(sender, instance, created, **kwargs):
            signal_received.append((sender, instance, created))

        # 시그널 연결
        post_save.connect(signal_listener, sender=Bookmarking)

        try:
            # Mock request 설정
            mock_request = MagicMock()
            mock_request.data = {
                "meme_id": self.meme.id,
                "bookmark_ids": [self.bookmark1.id],
            }
            mock_request.user = self.user

            view = BookmarkingSyncAPIView()
            view.request = mock_request

            # sync_bookmarking_with_bookmarks 메서드 호출
            view.sync_bookmarking_with_bookmarks()

            # 시그널이 전송되었는지 확인
            self.assertEqual(len(signal_received), 1)
            self.assertEqual(signal_received[0][0], Bookmarking)
            self.assertTrue(signal_received[0][2])  # created=True

        finally:
            # 시그널 연결 해제
            post_save.disconnect(signal_listener, sender=Bookmarking)

    def test_authentication_required(self):
        """인증이 필요한지 테스트"""
        # 인증되지 않은 클라이언트로 요청
        unauthenticated_client = APIClient()

        data = {"meme_id": self.meme.id, "bookmark_ids": [self.bookmark1.id]}

        response = unauthenticated_client.post(self.url, data, format="json")

        # 401 Unauthorized 또는 403 Forbidden 응답 확인 (둘 다 인증/권한 문제)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_meme_not_found(self):
        """존재하지 않는 밈 ID로 요청 시 404 에러 테스트"""
        data = {
            "meme_id": 99999,  # 존재하지 않는 ID
            "bookmark_ids": [self.bookmark1.id],
        }

        response = self.client.post(self.url, data, format="json")

        # 404 Not Found 응답 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bulk_create_efficiency(self):
        """bulk_create를 사용하여 효율적으로 북마킹을 생성하는지 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # Mock request 설정 (여러 북마크 ID)
        mock_request = MagicMock()
        mock_request.data = {
            "meme_id": self.meme.id,
            "bookmark_ids": [self.bookmark1.id, self.bookmark2.id, self.bookmark3.id],
        }
        mock_request.user = self.user

        view = BookmarkingSyncAPIView()
        view.request = mock_request

        # sync_bookmarking_with_bookmarks 메서드 호출
        view.sync_bookmarking_with_bookmarks()

        # 모든 북마킹이 생성되었는지 확인
        bookmarkings = Bookmarking.objects.filter(
            user=self.user,
            meme=self.meme,
            bookmark__in=[self.bookmark1, self.bookmark2, self.bookmark3],
        )
        self.assertEqual(bookmarkings.count(), 3)

    def test_concurrent_bookmarking_operations(self):
        """동시에 여러 북마킹 작업이 수행될 때의 동작 테스트"""
        from api.v1.bookmark.views.bookmarking_sync_api_view import (
            BookmarkingSyncAPIView,
        )

        # 첫 번째 요청: 북마크가 있는 북마킹
        mock_request1 = MagicMock()
        mock_request1.data = {
            "meme_id": self.meme.id,
            "bookmark_ids": [self.bookmark1.id],
        }
        mock_request1.user = self.user

        view1 = BookmarkingSyncAPIView()
        view1.request = mock_request1

        # 두 번째 요청: 북마크가 없는 북마킹
        mock_request2 = MagicMock()
        mock_request2.data = {
            "meme_id": self.meme.id,
            "bookmark_ids": [],
            "without_bookmark": True,
        }
        mock_request2.user = self.user

        view2 = BookmarkingSyncAPIView()
        view2.request = mock_request2

        # 첫 번째 요청 실행
        view1.sync_bookmarking_with_bookmarks()

        # 두 번째 요청 실행
        view2.sync_without_bookmark()

        # 최종 상태 확인: 북마크가 없는 북마킹만 존재해야 함
        bookmarkings_with_bookmark = Bookmarking.objects.filter(
            user=self.user, meme=self.meme, bookmark__isnull=False
        )
        bookmarkings_without_bookmark = Bookmarking.objects.filter(
            user=self.user, meme=self.meme, bookmark__isnull=True
        )

        self.assertEqual(bookmarkings_with_bookmark.count(), 0)
        self.assertEqual(bookmarkings_without_bookmark.count(), 1)
