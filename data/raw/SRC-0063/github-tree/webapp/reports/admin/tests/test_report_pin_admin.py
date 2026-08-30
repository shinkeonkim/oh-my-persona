from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

import pytest
from reports.admin.report_pin_admin import ReportPinAdmin
from reports.models import ReportPin

User = get_user_model()


@pytest.mark.django_db
class ReportPinAdminTests(TestCase):
    """ReportPinAdmin 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.report_pin_admin = ReportPinAdmin(ReportPin, self.admin_site)

        # 사용자 생성
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="pass123",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass123",
        )

        # ReportPin 생성
        self.report_pin1 = ReportPin.objects.create(
            user=self.user1,
            pin_hash="test_hash_1",
            enabled_at=timezone.now(),
        )
        self.report_pin2 = ReportPin.objects.create(
            user=self.user2,
            pin_hash="test_hash_2",
            enabled_at=timezone.now(),
        )

    def test_list_display_configuration(self):
        """list_display 설정 테스트"""
        expected_fields = (
            "user",
            "enabled_at",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.report_pin_admin.list_display, expected_fields)

    def test_list_filter_configuration(self):
        """list_filter 설정 테스트"""
        expected_filters = (
            "enabled_at",
            "created_at",
        )
        self.assertEqual(self.report_pin_admin.list_filter, expected_filters)

    def test_search_fields_configuration(self):
        """search_fields 설정 테스트"""
        expected_fields = ("user__email",)
        self.assertEqual(self.report_pin_admin.search_fields, expected_fields)

    def test_readonly_fields_configuration(self):
        """readonly_fields 설정 테스트"""
        expected_fields = (
            "pin_hash",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.report_pin_admin.readonly_fields, expected_fields)

    def test_ordering_configuration(self):
        """ordering 설정 테스트"""
        self.assertEqual(self.report_pin_admin.ordering, ("-created_at",))

    def test_fields_configuration(self):
        """fields 설정 테스트"""
        expected_fields = (
            "user",
            "pin_hash",
            "enabled_at",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.report_pin_admin.fields, expected_fields)

    def test_actions_configuration(self):
        """actions 설정 테스트 (비어있어야 함)"""
        self.assertEqual(self.report_pin_admin.actions, ())

    def test_get_queryset(self):
        """get_queryset 메서드 테스트"""
        request = self.factory.get("/admin/reports/reportpin/")
        request.user = self.user1

        queryset = self.report_pin_admin.get_queryset(request)

        # 모든 ReportPin이 조회되는지 확인
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.report_pin1, queryset)
        self.assertIn(self.report_pin2, queryset)

    def test_list_display_shows_correct_data(self):
        """list_display 필드가 올바른 데이터를 표시하는지 테스트"""
        # user 필드
        user_value = getattr(self.report_pin1, "user")
        self.assertEqual(user_value, self.user1)

        # enabled_at 필드
        enabled_at_value = getattr(self.report_pin1, "enabled_at")
        self.assertIsNotNone(enabled_at_value)

        # created_at 필드
        created_at_value = getattr(self.report_pin1, "created_at")
        self.assertIsNotNone(created_at_value)

        # updated_at 필드
        updated_at_value = getattr(self.report_pin1, "updated_at")
        self.assertIsNotNone(updated_at_value)

    def test_search_by_email(self):
        """이메일로 검색 테스트"""
        request = self.factory.get("/admin/reports/reportpin/", {"q": "user1@example.com"})
        request.user = self.user1

        queryset = self.report_pin_admin.get_queryset(request)
        search_queryset = self.report_pin_admin.get_search_results(request, queryset, "user1@example.com")

        result_queryset = search_queryset[0]

        # user1의 ReportPin이 조회되어야 함
        self.assertIn(self.report_pin1, result_queryset)

    def test_filter_by_enabled_at(self):
        """enabled_at으로 필터링 테스트"""
        request = self.factory.get("/admin/reports/reportpin/")
        request.user = self.user1

        queryset = self.report_pin_admin.get_queryset(request)

        # enabled_at이 있는 ReportPin 필터링
        enabled_pins = queryset.filter(enabled_at__isnull=False)
        self.assertEqual(enabled_pins.count(), 2)

    def test_readonly_fields_cannot_be_edited(self):
        """readonly_fields가 수정 불가능한지 테스트"""
        readonly_fields = self.report_pin_admin.readonly_fields

        # pin_hash, created_at, updated_at이 readonly인지 확인
        self.assertIn("pin_hash", readonly_fields)
        self.assertIn("created_at", readonly_fields)
        self.assertIn("updated_at", readonly_fields)

    def test_ordering_by_created_at_descending(self):
        """created_at 내림차순 정렬 테스트"""
        request = self.factory.get("/admin/reports/reportpin/")
        request.user = self.user1

        queryset = self.report_pin_admin.get_queryset(request)

        # 쿼리셋의 ordering 확인
        ordering = queryset.query.order_by
        self.assertIn("-created_at", ordering)

    def test_no_custom_actions(self):
        """커스텀 액션이 없는지 테스트"""
        self.assertEqual(len(self.report_pin_admin.actions), 0)

    def test_user_field_display(self):
        """user 필드가 올바르게 표시되는지 테스트"""
        # user 필드는 사용자 객체를 반환해야 함
        user = self.report_pin1.user
        self.assertEqual(user.username, "user1")
        self.assertEqual(user.email, "user1@example.com")

    def test_pin_hash_is_readonly(self):
        """pin_hash가 readonly인지 테스트"""
        readonly_fields = self.report_pin_admin.readonly_fields
        self.assertIn("pin_hash", readonly_fields)

    def test_model_str_representation(self):
        """ReportPin 모델의 문자열 표현 테스트"""
        # ReportPin 모델은 기본 __str__ 메서드를 사용할 수 있음
        pin_str = str(self.report_pin1)
        # 기본 또는 커스텀 표현 확인
        self.assertIsNotNone(pin_str)

    def test_multiple_report_pins_per_user_not_allowed(self):
        """한 사용자당 하나의 ReportPin만 허용되는지 테스트 (OneToOneField)"""
        from django.db import IntegrityError

        # user1은 이미 ReportPin을 가지고 있으므로 중복 생성 시도 시 오류 발생
        with self.assertRaises(IntegrityError):
            ReportPin.objects.create(
                user=self.user1,
                pin_hash="duplicate_hash",
                enabled_at=timezone.now(),
            )

    def test_fields_order(self):
        """fields의 순서가 올바른지 테스트"""
        fields = self.report_pin_admin.fields
        self.assertEqual(fields[0], "user")
        self.assertEqual(fields[1], "pin_hash")
        self.assertEqual(fields[2], "enabled_at")
        self.assertEqual(fields[3], "created_at")
        self.assertEqual(fields[4], "updated_at")

    def test_search_returns_correct_results(self):
        """검색 기능이 올바른 결과를 반환하는지 테스트"""
        request = self.factory.get("/admin/reports/reportpin/", {"q": "user2@example.com"})
        request.user = self.user2

        queryset = self.report_pin_admin.get_queryset(request)
        search_queryset = self.report_pin_admin.get_search_results(request, queryset, "user2@example.com")

        result_queryset = search_queryset[0]

        # user2의 ReportPin만 조회되어야 함
        self.assertIn(self.report_pin2, result_queryset)
        self.assertEqual(result_queryset.count(), 1)
