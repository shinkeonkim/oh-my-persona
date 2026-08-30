from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from matchmakings.models import Referral
from profiles.models import Gender, Profile

User = get_user_model()


class ReferralModelTest(TestCase):
    """Referral 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
        )
        Profile.objects.create(user=self.user, gender=Gender.MALE)

        self.referral_user = User.objects.create_user(
            username="referral_user",
            email="referral@test.com",
        )
        Profile.objects.create(user=self.referral_user, gender=Gender.FEMALE)

    def test_create_referral_success(self):
        """Referral이 정상적으로 생성되는지 테스트"""
        now = timezone.now()
        referral = Referral.objects.create(
            user=self.user,
            referral_user=self.referral_user,
            referred_at=now,
            referred_algorithm="TestAlgorithm",
        )

        self.assertIsNotNone(referral.id)
        self.assertEqual(referral.user, self.user)
        self.assertEqual(referral.referral_user, self.referral_user)
        self.assertEqual(referral.referred_at, now)
        self.assertEqual(referral.referred_algorithm, "TestAlgorithm")

    def test_referral_str_representation(self):
        """Referral의 문자열 표현이 올바른지 테스트"""
        referral = Referral.objects.create(
            user=self.user,
            referral_user=self.referral_user,
            referred_at=timezone.now(),
            referred_algorithm="TestAlgorithm",
        )

        str_repr = str(referral)
        self.assertIn(str(self.user), str_repr)
        self.assertIn(str(self.referral_user), str_repr)

    def test_referral_cascade_delete_on_user_delete(self):
        """user가 삭제되면 Referral도 삭제되는지 테스트"""
        referral = Referral.objects.create(
            user=self.user,
            referral_user=self.referral_user,
            referred_at=timezone.now(),
            referred_algorithm="TestAlgorithm",
        )

        referral_id = referral.id
        self.user.delete()

        self.assertFalse(Referral.objects.filter(id=referral_id).exists())

    def test_referral_cascade_delete_on_referral_user_delete(self):
        """referral_user가 삭제되면 Referral도 삭제되는지 테스트"""
        referral = Referral.objects.create(
            user=self.user,
            referral_user=self.referral_user,
            referred_at=timezone.now(),
            referred_algorithm="TestAlgorithm",
        )

        referral_id = referral.id
        self.referral_user.delete()

        self.assertFalse(Referral.objects.filter(id=referral_id).exists())

    def test_multiple_referrals_for_same_user(self):
        """동일한 user에 대해 여러 Referral이 생성될 수 있는지 테스트"""
        another_user = User.objects.create_user(
            username="another_user",
            email="another@test.com",
        )
        Profile.objects.create(user=another_user, gender=Gender.FEMALE)

        referral1 = Referral.objects.create(
            user=self.user,
            referral_user=self.referral_user,
            referred_at=timezone.now(),
            referred_algorithm="Algorithm1",
        )

        referral2 = Referral.objects.create(
            user=self.user,
            referral_user=another_user,
            referred_at=timezone.now(),
            referred_algorithm="Algorithm2",
        )

        self.assertNotEqual(referral1.id, referral2.id)
        self.assertEqual(Referral.objects.filter(user=self.user).count(), 2)

    def test_referral_related_name_received_referrals(self):
        """user의 related_name received_referrals이 올바르게 동작하는지 테스트"""
        referral = Referral.objects.create(
            user=self.user,
            referral_user=self.referral_user,
            referred_at=timezone.now(),
            referred_algorithm="TestAlgorithm",
        )

        received_referrals = self.user.received_referrals.all()
        self.assertEqual(received_referrals.count(), 1)
        self.assertIn(referral, received_referrals)

    def test_referral_related_name_suggested_referrals(self):
        """referral_user의 related_name suggested_referrals이 올바르게 동작하는지 테스트"""
        referral = Referral.objects.create(
            user=self.user,
            referral_user=self.referral_user,
            referred_at=timezone.now(),
            referred_algorithm="TestAlgorithm",
        )

        suggested_referrals = self.referral_user.suggested_referrals.all()
        self.assertEqual(suggested_referrals.count(), 1)
        self.assertIn(referral, suggested_referrals)

    def test_referral_different_algorithms(self):
        """서로 다른 알고리즘으로 Referral을 생성할 수 있는지 테스트"""
        another_user = User.objects.create_user(
            username="another_user",
            email="another@test.com",
        )
        Profile.objects.create(user=another_user, gender=Gender.FEMALE)

        referral1 = Referral.objects.create(
            user=self.user,
            referral_user=self.referral_user,
            referred_at=timezone.now(),
            referred_algorithm="AlgorithmA",
        )

        referral2 = Referral.objects.create(
            user=self.user,
            referral_user=another_user,
            referred_at=timezone.now(),
            referred_algorithm="AlgorithmB",
        )

        self.assertEqual(referral1.referred_algorithm, "AlgorithmA")
        self.assertEqual(referral2.referred_algorithm, "AlgorithmB")

    def test_referral_order_by_referred_at(self):
        """Referral을 referred_at으로 정렬할 수 있는지 테스트"""
        another_user = User.objects.create_user(
            username="another_user",
            email="another@test.com",
        )
        Profile.objects.create(user=another_user, gender=Gender.FEMALE)

        # 오래된 추천
        old_referral = Referral.objects.create(
            user=self.user,
            referral_user=self.referral_user,
            referred_at=timezone.now() - timezone.timedelta(days=1),
            referred_algorithm="TestAlgorithm",
        )

        # 최근 추천
        recent_referral = Referral.objects.create(
            user=self.user,
            referral_user=another_user,
            referred_at=timezone.now(),
            referred_algorithm="TestAlgorithm",
        )

        referrals = Referral.objects.filter(user=self.user).order_by("-referred_at")
        self.assertEqual(referrals.first().id, recent_referral.id)
        self.assertEqual(referrals.last().id, old_referral.id)
