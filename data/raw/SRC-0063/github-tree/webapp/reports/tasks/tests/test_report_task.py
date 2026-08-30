from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from celery.exceptions import Retry
from reports.models import Report
from reports.tasks.report_task import generate_report_task

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class GenerateReportTaskTests(TestCase):
    """generate_report_task Celery Task 테스트"""

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

    @patch("reports.tasks.report_task.ReportGenerationService.update_or_create_report")
    def test_generate_report_task_success(self, mock_service):
        """레포트 생성 성공 테스트"""
        # Mock service
        mock_report = Mock()
        mock_report.id = 123
        mock_service.return_value = mock_report

        # 실행
        result = generate_report_task(
            user_id=self.user.id,
            child_id=self.child.id,
        )

        # 검증
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Report generated successfully")
        self.assertEqual(result["report_id"], 123)

        # Service 호출 확인
        mock_service.assert_called_once_with(
            user=self.user,
            child=self.child,
        )

    def test_generate_report_task_user_not_found(self):
        """사용자를 찾을 수 없을 때 테스트"""
        # 존재하지 않는 사용자 ID
        invalid_user_id = 9999

        # 실행
        result = generate_report_task(
            user_id=invalid_user_id,
            child_id=self.child.id,
        )

        # 검증 - 최대 재시도 후 실패 반환
        self.assertFalse(result["success"])
        self.assertIn("Failed to generate report", result["message"])

    def test_generate_report_task_child_not_found(self):
        """아동을 찾을 수 없을 때 테스트"""
        # 존재하지 않는 아동 ID
        invalid_child_id = 9999

        # 실행
        result = generate_report_task(
            user_id=self.user.id,
            child_id=invalid_child_id,
        )

        # 검증 - 최대 재시도 후 실패 반환
        self.assertFalse(result["success"])
        self.assertIn("Failed to generate report", result["message"])

    @patch("reports.tasks.report_task.ReportGenerationService.update_or_create_report")
    def test_generate_report_task_service_error_with_retry(self, mock_service):
        """서비스 오류 발생 시 재시도 테스트"""
        # Mock service - 예외 발생
        mock_service.side_effect = Exception("Service error")

        # Mock task instance
        mock_task_instance = Mock()
        mock_task_instance.request.retries = 0
        mock_task_instance.max_retries = 3

        def mock_retry(exc):
            raise Retry(exc=exc)

        mock_task_instance.retry = mock_retry

        # 실행 및 검증 - Retry 예외 발생
        with self.assertRaises(Retry):
            generate_report_task(
                mock_task_instance,
                user_id=self.user.id,
                child_id=self.child.id,
            )

    @patch("reports.tasks.report_task.ReportGenerationService.update_or_create_report")
    def test_generate_report_task_max_retries_exceeded(self, mock_service):
        """최대 재시도 횟수 초과 테스트"""
        # Mock service - 예외 발생
        mock_service.side_effect = Exception("Persistent error")

        # Mock task instance - 최대 재시도 횟수 도달
        mock_task_instance = Mock()
        mock_task_instance.request.retries = 3
        mock_task_instance.max_retries = 3

        # 실행
        result = generate_report_task(
            mock_task_instance,
            user_id=self.user.id,
            child_id=self.child.id,
        )

        # 검증 - 실패 반환
        self.assertFalse(result["success"])
        self.assertIn("Failed to generate report after 3 retries", result["message"])

    @patch("reports.tasks.report_task.ReportGenerationService.update_or_create_report")
    def test_generate_report_task_creates_actual_report(self, mock_service):
        """실제 레포트 생성 확인 테스트"""
        # Mock service - 실제 레포트 반환
        report = Report.objects.create(
            user=self.user,
            child=self.child,
        )
        mock_service.return_value = report

        # 실행
        result = generate_report_task(
            user_id=self.user.id,
            child_id=self.child.id,
        )

        # 검증
        self.assertTrue(result["success"])
        self.assertEqual(result["report_id"], report.id)

        # DB에 레포트가 생성되었는지 확인
        self.assertTrue(
            Report.objects.filter(
                user=self.user,
                child=self.child,
            ).exists()
        )

    @patch("reports.tasks.report_task.ReportGenerationService.update_or_create_report")
    @patch("reports.tasks.report_task.logger")
    def test_generate_report_task_logs_success(self, mock_logger, mock_service):
        """성공 시 로그 기록 테스트"""
        # Mock service
        mock_report = Mock()
        mock_report.id = 456
        mock_service.return_value = mock_report

        # 실행
        generate_report_task(
            user_id=self.user.id,
            child_id=self.child.id,
        )

        # 검증 - 로그 호출 확인
        mock_logger.info.assert_called()

        # 로그 메시지 확인
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        log_messages = " ".join(log_calls)
        self.assertIn("Starting generate_report_task", log_messages)
        self.assertIn("generated successfully", log_messages)

    @patch("reports.tasks.report_task.ReportGenerationService.update_or_create_report")
    @patch("reports.tasks.report_task.logger")
    def test_generate_report_task_logs_error(self, mock_logger, mock_service):
        """오류 시 로그 기록 테스트"""
        # Mock service - 예외 발생
        mock_service.side_effect = Exception("Test error")

        # 실행
        generate_report_task(
            user_id=self.user.id,
            child_id=self.child.id,
        )

        # 검증 - 에러 로그 호출 확인
        mock_logger.error.assert_called()

    @patch("reports.tasks.report_task.ReportGenerationService.update_or_create_report")
    def test_generate_report_task_multiple_calls(self, mock_service):
        """여러 번 호출 테스트"""
        # Mock service
        mock_report1 = Mock()
        mock_report1.id = 100

        mock_report2 = Mock()
        mock_report2.id = 200

        mock_service.side_effect = [mock_report1, mock_report2]

        # 첫 번째 호출
        result1 = generate_report_task(
            user_id=self.user.id,
            child_id=self.child.id,
        )

        # 두 번째 호출
        result2 = generate_report_task(
            user_id=self.user.id,
            child_id=self.child.id,
        )

        # 검증
        self.assertTrue(result1["success"])
        self.assertEqual(result1["report_id"], 100)

        self.assertTrue(result2["success"])
        self.assertEqual(result2["report_id"], 200)

        # Service가 두 번 호출되었는지 확인
        self.assertEqual(mock_service.call_count, 2)

    @patch("reports.tasks.report_task.ReportGenerationService.update_or_create_report")
    def test_generate_report_task_return_structure(self, mock_service):
        """반환 값 구조 테스트"""
        # Mock service
        mock_report = Mock()
        mock_report.id = 789
        mock_service.return_value = mock_report

        # 실행
        result = generate_report_task(
            user_id=self.user.id,
            child_id=self.child.id,
        )

        # 검증 - 반환 값 구조 확인
        self.assertIn("success", result)
        self.assertIn("message", result)
        self.assertIn("report_id", result)

        self.assertIsInstance(result["success"], bool)
        self.assertIsInstance(result["message"], str)
        self.assertIsInstance(result["report_id"], int)

    @patch("reports.tasks.report_task.ReportGenerationService.update_or_create_report")
    def test_generate_report_task_error_return_structure(self, mock_service):
        """오류 시 반환 값 구조 테스트"""
        # Mock service - 예외 발생
        mock_service.side_effect = Exception("Test error")

        # 실행
        result = generate_report_task(
            user_id=self.user.id,
            child_id=self.child.id,
        )

        # 검증 - 반환 값 구조 확인
        self.assertIn("success", result)
        self.assertIn("message", result)

        self.assertFalse(result["success"])
        self.assertIsInstance(result["message"], str)

        # report_id는 실패 시 없을 수 있음
        self.assertNotIn("report_id", result)

    def test_task_configuration(self):
        """Task 설정 테스트"""
        # Task 메타데이터 확인
        self.assertEqual(generate_report_task.name, "reports.generate_report")
        self.assertEqual(generate_report_task.max_retries, 3)
        self.assertEqual(generate_report_task.default_retry_delay, 60)

    @patch("reports.tasks.report_task.ReportGenerationService.update_or_create_report")
    def test_generate_report_task_with_multiple_children(self, mock_service):
        """여러 아동에 대한 레포트 생성 테스트"""
        child2 = Child.objects.create(
            parent=self.user,
            name="Second Child",
            birth_year=2020,
            gender="F",
        )

        # Mock service
        mock_report1 = Mock()
        mock_report1.id = 111

        mock_report2 = Mock()
        mock_report2.id = 222

        mock_service.side_effect = [mock_report1, mock_report2]

        # 첫 번째 아동 레포트
        result1 = generate_report_task(
            user_id=self.user.id,
            child_id=self.child.id,
        )

        # 두 번째 아동 레포트
        result2 = generate_report_task(
            user_id=self.user.id,
            child_id=child2.id,
        )

        # 검증
        self.assertTrue(result1["success"])
        self.assertEqual(result1["report_id"], 111)

        self.assertTrue(result2["success"])
        self.assertEqual(result2["report_id"], 222)
