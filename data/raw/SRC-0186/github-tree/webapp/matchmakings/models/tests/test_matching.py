from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from matchmakings.models import Matching, MatchingStatus, Referral
from profiles.models import Gender, Profile

User = get_user_model()


class MatchingModelTest(TestCase):
    """Matching 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        # 남성 사용자 생성
        self.male_user = User.objects.create_user(
            username="male_user",
            email="male@test.com",
        )
        Profile.objects.create(user=self.male_user, gender=Gender.MALE)

        # 여성 사용자 생성
        self.female_user = User.objects.create_user(
            username="female_user",
            email="female@test.com",
        )
        Profile.objects.create(user=self.female_user, gender=Gender.FEMALE)

    def test_create_matching_success(self):
        """매칭이 정상적으로 생성되는지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        self.assertIsNotNone(matching.id)
        self.assertEqual(matching.sender, self.male_user)
        self.assertEqual(matching.receiver, self.female_user)
        self.assertEqual(matching.ticket_amount, 10)
        self.assertIsNotNone(matching.sent_at)
        self.assertIsNone(matching.received_at)
        self.assertIsNone(matching.rejected_at)
        self.assertIsNone(matching.expired_at)

    def test_matching_status_property_sent(self):
        """매칭 상태가 SENT인지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        self.assertEqual(matching.status, MatchingStatus.SENT)

    def test_matching_status_property_received(self):
        """매칭 상태가 RECEIVED인지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
            received_at=timezone.now(),
        )

        self.assertEqual(matching.status, MatchingStatus.RECEIVED)

    def test_matching_status_property_rejected(self):
        """매칭 상태가 REJECTED인지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
            rejected_at=timezone.now(),
        )

        self.assertEqual(matching.status, MatchingStatus.REJECTED)

    def test_accept_method(self):
        """accept 메서드가 정상적으로 동작하는지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        before_accept = timezone.now()
        matching.accept()
        after_accept = timezone.now()

        self.assertIsNotNone(matching.received_at)
        self.assertIsNone(matching.rejected_at)
        self.assertGreaterEqual(matching.received_at, before_accept)
        self.assertLessEqual(matching.received_at, after_accept)
        self.assertEqual(matching.status, MatchingStatus.RECEIVED)

    def test_reject_method(self):
        """reject 메서드가 정상적으로 동작하는지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        before_reject = timezone.now()
        matching.reject()
        after_reject = timezone.now()

        self.assertIsNone(matching.received_at)
        self.assertIsNotNone(matching.rejected_at)
        self.assertGreaterEqual(matching.rejected_at, before_reject)
        self.assertLessEqual(matching.rejected_at, after_reject)
        self.assertEqual(matching.status, MatchingStatus.REJECTED)

    def test_expire_method(self):
        """expire 메서드가 정상적으로 동작하는지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        before_expire = timezone.now()
        matching.expire()
        after_expire = timezone.now()

        self.assertIsNotNone(matching.expired_at)
        self.assertGreaterEqual(matching.expired_at, before_expire)
        self.assertLessEqual(matching.expired_at, after_expire)

    def test_accept_clears_rejected_at(self):
        """accept 메서드가 rejected_at을 None으로 설정하는지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
            rejected_at=timezone.now(),
        )

        matching.accept()

        self.assertIsNone(matching.rejected_at)
        self.assertIsNotNone(matching.received_at)

    def test_reject_clears_received_at(self):
        """reject 메서드가 received_at을 None으로 설정하는지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
            received_at=timezone.now(),
        )

        matching.reject()

        self.assertIsNone(matching.received_at)
        self.assertIsNotNone(matching.rejected_at)

    def test_unique_constraint_sender_receiver(self):
        """동일한 sender와 receiver로 중복 생성이 불가능한지 테스트"""
        Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        # 같은 sender와 receiver로 다시 생성 시도
        with self.assertRaises(Exception):  # IntegrityError
            Matching.objects.create(
                sender=self.male_user,
                receiver=self.female_user,
                ticket_amount=10,
                sent_at=timezone.now(),
            )

    def test_validation_fails_without_sender_gender(self):
        """sender의 성별이 없으면 검증 실패하는지 테스트"""
        user_without_gender = User.objects.create_user(
            username="no_gender",
            email="no_gender@test.com",
        )

        matching = Matching(
            sender=user_without_gender,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        with self.assertRaises(ValidationError) as context:
            matching.save()

        self.assertIn("sender", str(context.exception))

    def test_validation_fails_without_receiver_gender(self):
        """receiver의 성별이 없으면 검증 실패하는지 테스트"""
        user_without_gender = User.objects.create_user(
            username="no_gender",
            email="no_gender@test.com",
        )

        matching = Matching(
            sender=self.male_user,
            receiver=user_without_gender,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        with self.assertRaises(ValidationError) as context:
            matching.save()

        self.assertIn("receiver", str(context.exception))

    def test_validation_fails_same_gender(self):
        """sender와 receiver의 성별이 같으면 검증 실패하는지 테스트"""
        another_male_user = User.objects.create_user(
            username="another_male",
            email="another_male@test.com",
        )
        Profile.objects.create(user=another_male_user, gender=Gender.MALE)

        matching = Matching(
            sender=self.male_user,
            receiver=another_male_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        with self.assertRaises(ValidationError) as context:
            matching.save()

        self.assertIn("receiver", str(context.exception))
        self.assertIn("성별이 달라야", str(context.exception))

    def test_matching_with_referral(self):
        """Referral과 연결된 매칭이 정상적으로 생성되는지 테스트"""
        referral = Referral.objects.create(
            user=self.male_user,
            referral_user=self.female_user,
            referred_at=timezone.now(),
            referred_algorithm="TestAlgorithm",
        )

        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
            referral=referral,
        )

        self.assertEqual(matching.referral, referral)

    def test_matching_referral_set_null_on_delete(self):
        """Referral이 삭제되면 매칭의 referral이 None이 되는지 테스트"""
        referral = Referral.objects.create(
            user=self.male_user,
            referral_user=self.female_user,
            referred_at=timezone.now(),
            referred_algorithm="TestAlgorithm",
        )

        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
            referral=referral,
        )

        referral.delete()

        matching.refresh_from_db()
        self.assertIsNone(matching.referral)

    def test_matching_str_representation(self):
        """매칭의 문자열 표현이 올바른지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        str_repr = str(matching)
        self.assertIn(str(self.male_user), str_repr)
        self.assertIn(str(self.female_user), str_repr)

    def test_matching_cascade_delete_on_sender_delete(self):
        """sender가 삭제되면 매칭도 삭제되는지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        matching_id = matching.id
        self.male_user.delete()

        self.assertFalse(Matching.objects.filter(id=matching_id).exists())

    def test_matching_cascade_delete_on_receiver_delete(self):
        """receiver가 삭제되면 매칭도 삭제되는지 테스트"""
        matching = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        matching_id = matching.id
        self.female_user.delete()

        self.assertFalse(Matching.objects.filter(id=matching_id).exists())

    def test_multiple_matchings_between_different_users(self):
        """서로 다른 사용자 간 여러 매칭이 가능한지 테스트"""
        another_female = User.objects.create_user(
            username="another_female",
            email="another_female@test.com",
        )
        Profile.objects.create(user=another_female, gender=Gender.FEMALE)

        matching1 = Matching.objects.create(
            sender=self.male_user,
            receiver=self.female_user,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        matching2 = Matching.objects.create(
            sender=self.male_user,
            receiver=another_female,
            ticket_amount=10,
            sent_at=timezone.now(),
        )

        self.assertNotEqual(matching1.id, matching2.id)
        self.assertEqual(Matching.objects.filter(sender=self.male_user).count(), 2)
