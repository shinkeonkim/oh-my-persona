from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from api.v1.matchmakings.services import ReferralService

User = get_user_model()


class ReferralServiceTest(TestCase):
  """ReferralService 테스트 (Facade 패턴)"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = User.objects.create_user(
        username="test_user",
        email="test@test.com",
        remaining_referral_quota=5,
    )
    self.algorithm_type = "TestAlgorithm"

  @patch("api.v1.matchmakings.services.referral_service.ReferralCreationService.create_referral")
  def test_create_referral(self, mock_create):
    """추천 생성이 ReferralCreationService로 위임되는지 테스트"""
    mock_result = Mock()
    mock_create.return_value = mock_result

    result = ReferralService.create_referral(self.user, self.algorithm_type)

    mock_create.assert_called_once_with(self.user, self.algorithm_type)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.referral_service.ReferralQueryService.get_latest_referral")
  def test_get_latest_referral_without_algorithm_type(self, mock_get_latest):
    """알고리즘 타입 없이 최근 추천 조회가 ReferralQueryService로 위임되는지 테스트"""
    mock_result = Mock()
    mock_get_latest.return_value = mock_result

    result = ReferralService.get_latest_referral(self.user)

    mock_get_latest.assert_called_once_with(self.user, None)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.referral_service.ReferralQueryService.get_latest_referral")
  def test_get_latest_referral_with_algorithm_type(self, mock_get_latest):
    """알고리즘 타입과 함께 최근 추천 조회가 ReferralQueryService로 위임되는지 테스트"""
    mock_result = Mock()
    mock_get_latest.return_value = mock_result

    result = ReferralService.get_latest_referral(self.user, self.algorithm_type)

    mock_get_latest.assert_called_once_with(self.user, self.algorithm_type)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.referral_service.ReferralCreationService.create_referral")
  def test_create_referral_propagates_exceptions(self, mock_create):
    """ReferralCreationService에서 발생한 예외가 전파되는지 테스트"""
    from common.exceptions.custom_exceptions import ValidationError

    mock_create.side_effect = ValidationError(message="Test error")

    with self.assertRaises(ValidationError):
      ReferralService.create_referral(self.user, self.algorithm_type)

  @patch("api.v1.matchmakings.services.referral_service.ReferralQueryService.get_latest_referral")
  def test_get_latest_referral_propagates_exceptions(self, mock_get_latest):
    """ReferralQueryService에서 발생한 예외가 전파되는지 테스트"""
    from api.v1.matchmakings.exceptions import ReferralNotFoundError

    mock_get_latest.side_effect = ReferralNotFoundError(message="No referrals found")

    with self.assertRaises(ReferralNotFoundError):
      ReferralService.get_latest_referral(self.user)

  @patch("api.v1.matchmakings.services.referral_service.ReferralCreationService.create_referral")
  def test_create_referral_with_different_algorithms(self, mock_create):
    """다른 알고리즘 타입으로 추천 생성이 올바르게 위임되는지 테스트"""
    mock_result1 = Mock()
    mock_result2 = Mock()
    mock_create.side_effect = [mock_result1, mock_result2]

    # 첫 번째 알고리즘으로 생성
    result1 = ReferralService.create_referral(self.user, "Algorithm1")
    self.assertEqual(result1, mock_result1)

    # 두 번째 알고리즘으로 생성
    result2 = ReferralService.create_referral(self.user, "Algorithm2")
    self.assertEqual(result2, mock_result2)

    # 각각 올바른 인자로 호출되었는지 확인
    calls = mock_create.call_args_list
    self.assertEqual(calls[0][0], (self.user, "Algorithm1"))
    self.assertEqual(calls[1][0], (self.user, "Algorithm2"))

  @patch("api.v1.matchmakings.services.referral_service.ReferralQueryService.get_latest_referral")
  def test_get_latest_referral_returns_none_when_service_returns_none(self, mock_get_latest):
    """하위 서비스가 None을 반환할 때 올바르게 전달되는지 테스트"""
    mock_get_latest.return_value = None

    result = ReferralService.get_latest_referral(self.user)

    self.assertIsNone(result)

  @patch("api.v1.matchmakings.services.referral_service.ReferralCreationService.create_referral")
  def test_create_referral_returns_none_when_service_returns_none(self, mock_create):
    """하위 서비스가 None을 반환할 때 올바르게 전달되는지 테스트"""
    mock_create.return_value = None

    result = ReferralService.create_referral(self.user, self.algorithm_type)

    self.assertIsNone(result)

  @patch("api.v1.matchmakings.services.referral_service.ReferralCreationService.create_referral")
  @patch("api.v1.matchmakings.services.referral_service.ReferralQueryService.get_latest_referral")
  def test_both_methods_are_independent(self, mock_get_latest, mock_create):
    """두 메서드가 독립적으로 동작하는지 테스트"""
    mock_create_result = Mock()
    mock_get_result = Mock()
    mock_create.return_value = mock_create_result
    mock_get_latest.return_value = mock_get_result

    # create_referral 호출
    create_result = ReferralService.create_referral(self.user, self.algorithm_type)

    # get_latest_referral 호출
    get_result = ReferralService.get_latest_referral(self.user, self.algorithm_type)

    # 각각 올바른 서비스가 호출되었는지 확인
    mock_create.assert_called_once_with(self.user, self.algorithm_type)
    mock_get_latest.assert_called_once_with(self.user, self.algorithm_type)

    # 각각 올바른 결과를 반환하는지 확인
    self.assertEqual(create_result, mock_create_result)
    self.assertEqual(get_result, mock_get_result)

  def test_referral_service_is_static(self):
    """ReferralService의 메서드들이 static method인지 테스트"""
    # 인스턴스 생성 없이 호출 가능한지 확인
    self.assertTrue(callable(ReferralService.create_referral))
    self.assertTrue(callable(ReferralService.get_latest_referral))

    # static method인지 확인
    import inspect

    self.assertTrue(isinstance(inspect.getattr_static(ReferralService, "create_referral"), staticmethod))
    self.assertTrue(isinstance(inspect.getattr_static(ReferralService, "get_latest_referral"), staticmethod))
