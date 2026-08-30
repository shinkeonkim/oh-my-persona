from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

import pytest
from reports.choices import ReportStatusChoice
from reports.models import Report

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class ReportModelTests(TestCase):
    """Report 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.child = Child.objects.create(
            parent=self.user,
            name="Test Child",
            birth_year=2020,
            gender="M",
        )

    def test_create_report(self):
        """레포트 생성 테스트"""
        report = Report.objects.create(
            user=self.user,
            child=self.child,
            concentration_score=75,
        )

        self.assertEqual(report.user, self.user)
        self.assertEqual(report.child, self.child)
        self.assertEqual(report.concentration_score, 75)
        self.assertEqual(report.status, ReportStatusChoice.NO_GAMES_PLAYED)

    def test_report_default_status(self):
        """레포트 기본 상태 테스트"""
        report = Report.objects.create(
            user=self.user,
            child=self.child,
        )

        self.assertEqual(report.status, ReportStatusChoice.NO_GAMES_PLAYED)

    def test_report_default_concentration_score(self):
        """레포트 기본 집중력 점수 테스트"""
        report = Report.objects.create(
            user=self.user,
            child=self.child,
        )

        self.assertEqual(report.concentration_score, 0)

    def test_unique_user_child_constraint(self):
        """사용자와 아동 조합의 유일성 제약 테스트"""
        Report.objects.create(
            user=self.user,
            child=self.child,
        )

        with self.assertRaises(IntegrityError):
            Report.objects.create(
                user=self.user,
                child=self.child,
            )

    def test_get_or_create_for_user_child_creates_new(self):
        """get_or_create_for_user_child 메서드 - 새로 생성"""
        report, created = Report.objects.get_or_create_for_user_child(
            user=self.user,
            child=self.child,
        )

        self.assertTrue(created)
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.child, self.child)

    def test_get_or_create_for_user_child_gets_existing(self):
        """get_or_create_for_user_child 메서드 - 기존 조회"""
        existing_report = Report.objects.create(
            user=self.user,
            child=self.child,
            concentration_score=80,
        )

        report, created = Report.objects.get_or_create_for_user_child(
            user=self.user,
            child=self.child,
        )

        self.assertFalse(created)
        self.assertEqual(report.id, existing_report.id)
        self.assertEqual(report.concentration_score, 80)

    def test_report_str_representation(self):
        """레포트 문자열 표현 테스트"""
        report = Report.objects.create(
            user=self.user,
            child=self.child,
        )

        expected = f"{self.user.username} - {self.child.name} 레포트"
        self.assertEqual(str(report), expected)

    def test_multiple_reports_different_users(self):
        """다른 사용자들의 레포트 생성 테스트"""
        user2 = User.objects.create_user(
            username="user2",
            password="pass123",
        )
        child2 = Child.objects.create(
            parent=user2,
            name="Second Child",
            birth_year=2020,
            gender="F",
        )

        report1 = Report.objects.create(
            user=self.user,
            child=self.child,
        )
        report2 = Report.objects.create(
            user=user2,
            child=child2,
        )

        self.assertNotEqual(report1.id, report2.id)
        self.assertNotEqual(report1.user, report2.user)
        self.assertNotEqual(report1.child, report2.child)

    def test_report_status_update(self):
        """레포트 상태 업데이트 테스트"""
        report = Report.objects.create(
            user=self.user,
            child=self.child,
        )

        report.status = ReportStatusChoice.GENERATING
        report.save()

        report.refresh_from_db()
        self.assertEqual(report.status, ReportStatusChoice.GENERATING)

        report.status = ReportStatusChoice.COMPLETED
        report.save()

        report.refresh_from_db()
        self.assertEqual(report.status, ReportStatusChoice.COMPLETED)

    def test_report_concentration_score_boundaries(self):
        """집중력 점수 경계값 테스트"""
        # 최소값
        report_min = Report.objects.create(
            user=self.user,
            child=self.child,
            concentration_score=0,
        )
        self.assertEqual(report_min.concentration_score, 0)

        # 최대값
        user2 = User.objects.create_user(username="user2", password="pass")
        child_for_user2 = Child.objects.create(
            parent=user2,
            name="Child for User2",
            birth_year=2020,
            gender="M",
        )
        report_max = Report.objects.create(
            user=user2,
            child=child_for_user2,
            concentration_score=100,
        )
        self.assertEqual(report_max.concentration_score, 100)

    def test_report_ordering(self):
        """레포트 정렬 테스트 (updated_at 역순)"""
        user2 = User.objects.create_user(username="user2_order", password="pass")
        child2 = Child.objects.create(
            parent=user2,
            name="Child 2",
            birth_year=2020,
            gender="F",
        )
        user3 = User.objects.create_user(username="user3_order", password="pass")
        child3 = Child.objects.create(
            parent=user3,
            name="Child 3",
            birth_year=2020,
            gender="M",
        )

        Report.objects.create(user=self.user, child=self.child)
        Report.objects.create(user=user2, child=child2)
        report3 = Report.objects.create(user=user3, child=child3)

        # report3이 가장 최근에 생성되었으므로 첫 번째
        reports = Report.objects.all()
        self.assertEqual(reports[0].id, report3.id)
