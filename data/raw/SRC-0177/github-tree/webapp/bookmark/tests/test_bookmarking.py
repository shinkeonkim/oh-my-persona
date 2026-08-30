from bookmark.models import Bookmark, Bookmarking
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from meme.models import Meme

User = get_user_model()


class BookmarkingModelTest(TestCase):
    def setUp(self):
        """테스트에 필요한 기본 데이터를 생성합니다."""
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

        self.meme = Meme.objects.create(
            type="Text",
            title="Test Meme",
            description="This is a test meme",
            creator=self.user,
        )

        self.bookmark = Bookmark.objects.create(title="Test Bookmark", user=self.user)

    def test_bookmarking_creation(self):
        """Bookmarking 모델 생성 테스트"""
        bookmarking = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark
        )

        self.assertEqual(bookmarking.user, self.user)
        self.assertEqual(bookmarking.meme, self.meme)
        self.assertEqual(bookmarking.bookmark, self.bookmark)
        self.assertIsNotNone(bookmarking.created_at)
        self.assertIsNotNone(bookmarking.updated_at)

    def test_bookmarking_without_bookmark(self):
        """북마크 없이 Bookmarking 생성 테스트"""
        bookmarking = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=None
        )

        self.assertIsNone(bookmarking.bookmark)
        self.assertEqual(bookmarking.user, self.user)
        self.assertEqual(bookmarking.meme, self.meme)

    def test_bookmarking_str_representation(self):
        """Bookmarking 모델의 문자열 표현 테스트"""
        bookmarking = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark
        )

        expected_str = f"{self.bookmark} - {self.meme}"
        self.assertEqual(str(bookmarking), expected_str)

    def test_bookmarking_str_representation_without_bookmark(self):
        """북마크가 없는 경우 문자열 표현 테스트"""
        bookmarking = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=None
        )

        expected_str = f"None - {self.meme}"
        self.assertEqual(str(bookmarking), expected_str)

    def test_unique_user_meme_bookmark_constraint(self):
        """사용자-밈-북마크 조합의 유니크 제약조건 테스트"""
        # 첫 번째 bookmarking 생성
        Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark
        )

        # 동일한 사용자-밈-북마크 조합으로 다시 생성 시도
        with self.assertRaises(IntegrityError):
            Bookmarking.objects.create(
                user=self.user, meme=self.meme, bookmark=self.bookmark
            )

    def test_same_user_different_bookmarks_same_meme(self):
        """동일 사용자가 같은 밈을 다른 북마크에 추가하는 경우 테스트"""
        second_bookmark = Bookmark.objects.create(
            title="Second Bookmark", user=self.user
        )

        # 첫 번째 bookmarking 생성
        Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark
        )

        # 같은 사용자가 같은 밈을 다른 북마크에 추가
        second_bookmarking = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=second_bookmark
        )

        self.assertEqual(second_bookmarking.user, self.user)
        self.assertEqual(second_bookmarking.meme, self.meme)
        self.assertEqual(second_bookmarking.bookmark, second_bookmark)

    def test_save_method_sets_user_from_bookmark(self):
        """save 메서드에서 북마크의 사용자를 자동으로 설정하는지 테스트"""
        bookmarking = Bookmarking(meme=self.meme, bookmark=self.bookmark)

        # user를 명시적으로 설정하지 않음
        bookmarking.save()

        # save 메서드에서 자동으로 bookmark.user를 설정했는지 확인
        self.assertEqual(bookmarking.user, self.bookmark.user)
        self.assertEqual(bookmarking.user, self.user)

    def test_save_method_without_bookmark(self):
        """북마크가 없는 경우 save 메서드 테스트"""
        bookmarking = Bookmarking(user=self.user, meme=self.meme, bookmark=None)

        # 북마크가 없는 경우 user를 명시적으로 설정해야 함
        bookmarking.save()

        self.assertEqual(bookmarking.user, self.user)
        self.assertIsNone(bookmarking.bookmark)


class BookmarkingQuerySetTest(TestCase):
    def setUp(self):
        """테스트에 필요한 기본 데이터를 생성합니다."""
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

        self.meme1 = Meme.objects.create(
            type="Text",
            title="Test Meme 1",
            description="This is a test meme 1",
            creator=self.user,
        )

        self.meme2 = Meme.objects.create(
            type="Text",
            title="Test Meme 2",
            description="This is a test meme 2",
            creator=self.user,
        )

        self.bookmark = Bookmark.objects.create(title="Test Bookmark", user=self.user)

        # 북마크가 있는 bookmarking
        self.bookmarking_with_bookmark = Bookmarking.objects.create(
            user=self.user, meme=self.meme1, bookmark=self.bookmark
        )

        # 북마크가 없는 bookmarking
        self.bookmarking_without_bookmark = Bookmarking.objects.create(
            user=self.user, meme=self.meme2, bookmark=None
        )

    def test_with_bookmark_queryset_method(self):
        """with_bookmark 쿼리셋 메서드 테스트"""
        bookmarkings_with_bookmark = Bookmarking.objects.with_bookmark()

        self.assertIn(self.bookmarking_with_bookmark, bookmarkings_with_bookmark)
        self.assertNotIn(self.bookmarking_without_bookmark, bookmarkings_with_bookmark)
        self.assertEqual(bookmarkings_with_bookmark.count(), 1)

    def test_without_bookmark_queryset_method(self):
        """without_bookmark 쿼리셋 메서드 테스트"""
        bookmarkings_without_bookmark = Bookmarking.objects.without_bookmark()

        self.assertIn(self.bookmarking_without_bookmark, bookmarkings_without_bookmark)
        self.assertNotIn(self.bookmarking_with_bookmark, bookmarkings_without_bookmark)
        self.assertEqual(bookmarkings_without_bookmark.count(), 1)

    def test_queryset_methods_chain(self):
        """쿼리셋 메서드 체이닝 테스트"""
        # with_bookmark와 without_bookmark를 연속으로 사용
        with_bookmark_count = Bookmarking.objects.with_bookmark().count()
        without_bookmark_count = Bookmarking.objects.without_bookmark().count()

        self.assertEqual(with_bookmark_count, 1)
        self.assertEqual(without_bookmark_count, 1)

        # 전체 bookmarking 수와 비교
        total_count = Bookmarking.objects.count()
        self.assertEqual(total_count, with_bookmark_count + without_bookmark_count)


class BookmarkingModelManagerTest(TestCase):
    def setUp(self):
        """테스트에 필요한 기본 데이터를 생성합니다."""
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

        self.meme = Meme.objects.create(
            type="Text",
            title="Test Meme",
            description="This is a test meme",
            creator=self.user,
        )

        self.bookmark = Bookmark.objects.create(title="Test Bookmark", user=self.user)

    def test_manager_get_queryset(self):
        """매니저의 get_queryset 메서드 테스트"""
        bookmarking = Bookmarking.objects.create(
            user=self.user, meme=self.meme, bookmark=self.bookmark
        )

        # 매니저를 통해 쿼리셋 가져오기
        queryset = Bookmarking.objects.all()

        self.assertIn(bookmarking, queryset)
        self.assertEqual(queryset.count(), 1)

    def test_manager_use_for_related_fields(self):
        """매니저의 use_for_related_fields 설정 테스트"""
        self.assertTrue(Bookmarking.objects.use_for_related_fields)


class BookmarkingConstraintsTest(TestCase):
    def setUp(self):
        """테스트에 필요한 기본 데이터를 생성합니다."""
        self.user1 = User.objects.create_user(
            email="user1@example.com", username="user1", password="testpass123"
        )

        self.user2 = User.objects.create_user(
            email="user2@example.com", username="user2", password="testpass123"
        )

        self.meme1 = Meme.objects.create(
            type="Text",
            title="Test Meme 1",
            description="This is a test meme 1",
            creator=self.user1,
        )

        self.meme2 = Meme.objects.create(
            type="Text",
            title="Test Meme 2",
            description="This is a test meme 2",
            creator=self.user1,
        )

        self.meme3 = Meme.objects.create(
            type="Text",
            title="Test Meme 3",
            description="This is a test meme 3",
            creator=self.user1,
        )

        self.bookmark1 = Bookmark.objects.create(title="Bookmark 1", user=self.user1)

        self.bookmark2 = Bookmark.objects.create(title="Bookmark 2", user=self.user2)

        self.bookmark3 = Bookmark.objects.create(title="Bookmark 3", user=self.user1)

    def test_constraints_allow_different_combinations(self):
        """제약조건이 다른 조합을 허용하는지 테스트"""
        # 첫 번째 조합 생성 (user1, meme1, bookmark1)
        bookmarking1 = Bookmarking.objects.create(
            user=self.user1, meme=self.meme1, bookmark=self.bookmark1
        )

        # 두 번째 조합 생성 (user2, meme2, bookmark2) - 각자 자신의 북마크 사용
        bookmarking2 = Bookmarking.objects.create(
            user=self.user2, meme=self.meme2, bookmark=self.bookmark2
        )

        # 세 번째 조합 생성 (user1, meme2, bookmark3) - user1이 자신의 다른 북마크 사용
        bookmarking3 = Bookmarking.objects.create(
            user=self.user1, meme=self.meme2, bookmark=self.bookmark3
        )

        self.assertNotEqual(bookmarking1.id, bookmarking2.id)
        self.assertNotEqual(bookmarking1.id, bookmarking3.id)
        self.assertNotEqual(bookmarking2.id, bookmarking3.id)

        # 모든 bookmarking이 생성되었는지 확인
        self.assertEqual(Bookmarking.objects.count(), 3)

    def test_unique_user_meme_bookmark_constraint_violation(self):
        """사용자-밈-북마크 유니크 제약조건 위반 테스트"""
        # 첫 번째 bookmarking 생성
        Bookmarking.objects.create(
            user=self.user1, meme=self.meme1, bookmark=self.bookmark1
        )

        # 동일한 사용자-밈-북마크 조합으로 다시 생성 시도
        with self.assertRaises(IntegrityError):
            Bookmarking.objects.create(
                user=self.user1, meme=self.meme1, bookmark=self.bookmark1
            )

    def test_save_method_enforces_bookmark_ownership(self):
        """save 메서드가 북마크 소유권을 강제하는지 테스트"""
        # user2가 user1의 북마크를 사용하려고 시도
        bookmarking = Bookmarking.objects.create(
            user=self.user2,  # user2로 설정
            meme=self.meme1,
            bookmark=self.bookmark1,  # user1의 북마크
        )

        # save 메서드에서 자동으로 bookmark의 소유자로 변경되어야 함
        self.assertEqual(bookmarking.user, self.user1)  # user1으로 변경됨
        self.assertEqual(bookmarking.bookmark, self.bookmark1)
        self.assertEqual(bookmarking.meme, self.meme1)

    def test_unique_user_meme_bookmark_constraint_allows_different_bookmarks(self):
        """동일 사용자가 같은 밈을 다른 북마크에 추가할 수 있는지 테스트"""
        # 첫 번째 bookmarking 생성
        Bookmarking.objects.create(
            user=self.user1, meme=self.meme1, bookmark=self.bookmark1
        )

        # 같은 사용자가 같은 밈을 다른 북마크에 추가
        bookmarking2 = Bookmarking.objects.create(
            user=self.user1, meme=self.meme1, bookmark=self.bookmark3
        )

        self.assertEqual(bookmarking2.user, self.user1)
        self.assertEqual(bookmarking2.meme, self.meme1)
        self.assertEqual(bookmarking2.bookmark, self.bookmark3)

    def test_null_bookmarks_allow_multiple_entries(self):
        """PostgreSQL에서 NULL 북마크는 여러 개 허용되는지 테스트"""
        # 첫 번째 bookmarking 생성 (북마크 없음)
        bookmarking1 = Bookmarking.objects.create(
            user=self.user1, meme=self.meme1, bookmark=None
        )

        # 동일한 사용자-밈 조합으로 북마크 없이 다시 생성
        # PostgreSQL에서 NULL 값들은 서로 다른 것으로 간주되므로 허용됨
        bookmarking2 = Bookmarking.objects.create(
            user=self.user1, meme=self.meme1, bookmark=None
        )

        self.assertNotEqual(bookmarking1.id, bookmarking2.id)
        self.assertEqual(bookmarking1.user, bookmarking2.user)
        self.assertEqual(bookmarking1.meme, bookmarking2.meme)
        self.assertIsNone(bookmarking1.bookmark)
        self.assertIsNone(bookmarking2.bookmark)

    def test_different_users_can_bookmark_same_meme_without_bookmark(self):
        """다른 사용자가 동일한 밈에 대해 북마크 없이 추가할 수 있는지 테스트"""
        # 첫 번째 bookmarking 생성 (북마크 없음)
        Bookmarking.objects.create(user=self.user1, meme=self.meme1, bookmark=None)

        # 다른 사용자가 동일한 밈에 대해 북마크 없이 추가 (허용되어야 함)
        bookmarking2 = Bookmarking.objects.create(
            user=self.user2, meme=self.meme1, bookmark=None
        )

        self.assertNotEqual(bookmarking2.user, self.user1)
        self.assertEqual(bookmarking2.meme, self.meme1)
        self.assertIsNone(bookmarking2.bookmark)


class BookmarkingIndexTest(TestCase):
    def setUp(self):
        """테스트에 필요한 기본 데이터를 생성합니다."""
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

        self.meme = Meme.objects.create(
            type="Text",
            title="Test Meme",
            description="This is a test meme",
            creator=self.user,
        )

        self.bookmark = Bookmark.objects.create(title="Test Bookmark", user=self.user)

    def test_index_exists(self):
        """인덱스가 존재하는지 테스트"""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'bookmarkings'
                AND indexname LIKE '%meme_bookmark%'
            """
            )
            indexes = cursor.fetchall()

            # 인덱스가 존재하는지 확인
            self.assertTrue(len(indexes) > 0)
