from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

import pytest

from users.admin.child_admin import ChildAdmin
from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class ChildAdminTests(TestCase):
    """ChildAdmin 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.child_admin = ChildAdmin(Child, self.admin_site)

        # 사용자 생성 (각 부모당 한 명의 자녀만 생성 가능 - OneToOneField)
        self.parent1 = User.objects.create_user(
            username="parent1",
            email="parent1@example.com",
            password="pass123",
        )
        self.parent2 = User.objects.create_user(
            username="parent2",
            email="parent2@example.com",
            password="pass123",
        )
        self.parent3 = User.objects.create_user(
            username="parent3",
            email="parent3@example.com",
            password="pass123",
        )

        # 자녀 생성 (각 부모당 하나씩)
        self.child1 = Child.objects.create(
            parent=self.parent1,
            name="Child 1",
            birth_year=2020,
            gender="M",
        )
        self.child2 = Child.objects.create(
            parent=self.parent2,
            name="Child 2",
            birth_year=2021,
            gender="F",
        )
        self.child3 = Child.objects.create(
            parent=self.parent3,
            name="Child 3",
            birth_year=2019,
            gender="M",
        )

    def test_list_display_configuration(self):
        """list_display 설정 테스트"""
        expected_fields = (
            "parent",
            "name",
            "birth_year",
            "gender",
        )
        self.assertEqual(self.child_admin.list_display, expected_fields)

    def test_list_filter_configuration(self):
        """list_filter 설정 테스트"""
        expected_filters = (
            "gender",
            "created_at",
        )
        self.assertEqual(self.child_admin.list_filter, expected_filters)

    def test_search_fields_configuration(self):
        """search_fields 설정 테스트"""
        expected_fields = (
            "parent__email",
            "parent__username",
            "name",
        )
        self.assertEqual(self.child_admin.search_fields, expected_fields)

    def test_readonly_fields_configuration(self):
        """readonly_fields 설정 테스트"""
        expected_fields = (
            "parent",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.child_admin.readonly_fields, expected_fields)

    def test_ordering_configuration(self):
        """ordering 설정 테스트"""
        self.assertEqual(self.child_admin.ordering, ("-created_at",))

    def test_fieldsets_configuration(self):
        """fieldsets 설정 테스트"""
        expected_fieldsets = (
            (
                None,
                {
                    "fields": (
                        "parent",
                        "name",
                        "birth_year",
                        "gender",
                    ),
                },
            ),
            (
                "추가 정보",
                {
                    "fields": (
                        "created_at",
                        "updated_at",
                    ),
                },
            ),
        )
        self.assertEqual(self.child_admin.fieldsets, expected_fieldsets)

    def test_actions_configuration(self):
        """actions 설정 테스트 (비어있어야 함)"""
        self.assertEqual(self.child_admin.actions, ())

    def test_get_queryset(self):
        """get_queryset 메서드 테스트"""
        request = self.factory.get("/admin/users/child/")
        request.user = self.parent1

        queryset = self.child_admin.get_queryset(request)

        # 모든 자녀가 조회되는지 확인
        self.assertEqual(queryset.count(), 3)

    def test_list_display_shows_correct_data(self):
        """list_display 필드가 올바른 데이터를 표시하는지 테스트"""
        # parent 필드
        parent_value = getattr(self.child1, "parent")
        self.assertEqual(parent_value, self.parent1)

        # name 필드
        name_value = getattr(self.child1, "name")
        self.assertEqual(name_value, "Child 1")

        # birth_year 필드
        birth_year_value = getattr(self.child1, "birth_year")
        self.assertEqual(birth_year_value, 2020)

        # gender 필드
        gender_value = getattr(self.child1, "gender")
        self.assertEqual(gender_value, "M")

    def test_search_by_parent_email(self):
        """부모 이메일로 검색 테스트"""
        request = self.factory.get("/admin/users/child/", {"q": "parent1@example.com"})
        request.user = self.parent1

        queryset = self.child_admin.get_queryset(request)
        search_queryset = self.child_admin.get_search_results(request, queryset, "parent1@example.com")

        # search_results는 (queryset, use_distinct) 튜플 반환
        result_queryset = search_queryset[0]

        # parent1의 자녀가 조회되어야 함
        self.assertIn(self.child1, result_queryset)

    def test_search_by_parent_username(self):
        """부모 사용자명으로 검색 테스트"""
        request = self.factory.get("/admin/users/child/", {"q": "parent2"})
        request.user = self.parent2

        queryset = self.child_admin.get_queryset(request)
        search_queryset = self.child_admin.get_search_results(request, queryset, "parent2")

        result_queryset = search_queryset[0]

        # parent2의 자녀가 조회되어야 함
        self.assertIn(self.child2, result_queryset)

    def test_search_by_child_name(self):
        """자녀 이름으로 검색 테스트"""
        request = self.factory.get("/admin/users/child/", {"q": "Child 1"})
        request.user = self.parent1

        queryset = self.child_admin.get_queryset(request)
        search_queryset = self.child_admin.get_search_results(request, queryset, "Child 1")

        result_queryset = search_queryset[0]

        # 해당 이름의 자녀만 조회되어야 함
        self.assertIn(self.child1, result_queryset)

    def test_filter_by_gender(self):
        """성별로 필터링 테스트"""
        request = self.factory.get("/admin/users/child/")
        request.user = self.parent1

        queryset = self.child_admin.get_queryset(request)

        # 남아 필터링
        male_children = queryset.filter(gender="M")
        self.assertEqual(male_children.count(), 2)
        self.assertIn(self.child1, male_children)
        self.assertIn(self.child3, male_children)

        # 여아 필터링
        female_children = queryset.filter(gender="F")
        self.assertEqual(female_children.count(), 1)
        self.assertIn(self.child2, female_children)

    def test_readonly_fields_cannot_be_edited(self):
        """readonly_fields가 수정 불가능한지 테스트"""
        readonly_fields = self.child_admin.readonly_fields

        # parent, created_at, updated_at이 readonly인지 확인
        self.assertIn("parent", readonly_fields)
        self.assertIn("created_at", readonly_fields)
        self.assertIn("updated_at", readonly_fields)

    def test_ordering_by_created_at_descending(self):
        """created_at 내림차순 정렬 테스트"""
        request = self.factory.get("/admin/users/child/")
        request.user = self.parent1

        queryset = self.child_admin.get_queryset(request)

        # 쿼리셋의 ordering 확인
        ordering = queryset.query.order_by
        self.assertIn("-created_at", ordering)

    def test_fieldsets_structure(self):
        """fieldsets 구조 테스트"""
        fieldsets = self.child_admin.fieldsets

        # 첫 번째 fieldset (기본 정보)
        first_fieldset = fieldsets[0]
        self.assertIsNone(first_fieldset[0])  # 제목 없음
        self.assertIn("parent", first_fieldset[1]["fields"])
        self.assertIn("name", first_fieldset[1]["fields"])
        self.assertIn("birth_year", first_fieldset[1]["fields"])
        self.assertIn("gender", first_fieldset[1]["fields"])

        # 두 번째 fieldset (추가 정보)
        second_fieldset = fieldsets[1]
        self.assertEqual(second_fieldset[0], "추가 정보")
        self.assertIn("created_at", second_fieldset[1]["fields"])
        self.assertIn("updated_at", second_fieldset[1]["fields"])

    def test_no_custom_actions(self):
        """커스텀 액션이 없는지 테스트"""
        self.assertEqual(len(self.child_admin.actions), 0)

    def test_model_str_representation(self):
        """Child 모델의 문자열 표현 테스트"""
        # Child 모델은 기본 __str__ 메서드를 사용 (Django의 기본 동작)
        child_str = str(self.child1)
        # 기본 표현은 "Child object (id)" 형식
        self.assertIn("Child object", child_str)
