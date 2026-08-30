from django.core.exceptions import ValidationError
from django.test import TestCase

from api.v1.profiles.serializers.my_profile_serializer import MyProfileSerializer
from common.choices import Gender, Mbti
from profiles.factories import JobCategoryFactory, JobFactory, JobInfoFactory
from profiles.models import JobInfo
from users.factories import UserFactory


class MyProfileSerializerTestCase(TestCase):
    """MyProfileSerializer 테스트 케이스"""

    def setUp(self):
        """테스트 데이터 설정"""
        # Factory를 사용한 테스트 데이터 생성
        self.job_category = JobCategoryFactory(name="IT/개발")
        self.job = JobFactory(name="백엔드 개발자", job_category=self.job_category)
        self.other_job_category = JobCategoryFactory(name="디자인")
        self.other_job = JobFactory(name="UI/UX 디자이너", job_category=self.other_job_category)

        self.user = UserFactory(confirm_user=True)
        self.profile = self.user.profile
        self.profile.job_info = JobInfoFactory(job=self.job)
        self.profile.save()

    def test_serializer_creation(self):
        """Serializer 생성 테스트"""
        serializer = MyProfileSerializer()
        self.assertIsInstance(serializer, MyProfileSerializer)

    def test_serializer_fields(self):
        """Serializer 필드 확인 테스트"""
        serializer = MyProfileSerializer()
        expected_fields = [
            "id",
            "mbti",
            "region",
            "city",
            "job_info",
            "gender",
            "birth_time",
            "introduction",
            "one_liner",
            "tmi",
            "saju_profile",
        ]

        for field in expected_fields:
            self.assertIn(field, serializer.fields)

    def test_serializer_read_only_fields(self):
        """Serializer read_only 필드 확인 테스트"""
        serializer = MyProfileSerializer()
        read_only_fields = ["id"]

        for field in read_only_fields:
            self.assertTrue(serializer.fields[field].read_only)

    def test_serialize_profile_without_job_info(self):
        """JobInfo가 없는 프로필 직렬화 테스트"""
        # 기존 프로필 사용 (JobInfo 없이)
        profile = self.profile
        profile.job_info = None
        profile.save()

        # 직렬화
        serializer = MyProfileSerializer(profile)
        data = serializer.data

        # 검증
        self.assertEqual(data["mbti"], profile.mbti)
        self.assertEqual(data["gender"], profile.gender)
        self.assertEqual(data["region"], profile.region)
        self.assertEqual(data["city"], profile.city)
        self.assertEqual(data["introduction"], profile.introduction)
        self.assertIsNone(data["job_info"])

    def test_serialize_profile_with_job_info(self):
        """JobInfo가 있는 프로필 직렬화 테스트"""
        # Factory를 사용한 프로필과 JobInfo 생성
        # 기존 프로필 사용 (JobInfo 포함)
        profile = self.profile

        # 직렬화
        serializer = MyProfileSerializer(profile)
        data = serializer.data

        # 검증
        self.assertEqual(data["mbti"], profile.mbti)  # 실제 프로필 값
        self.assertEqual(data["gender"], profile.gender)  # 실제 프로필 값
        self.assertEqual(data["region"], profile.region)
        self.assertEqual(data["city"], profile.city)

        # JobInfo 검증
        job_info_data = data["job_info"]
        self.assertIsNotNone(job_info_data)
        self.assertEqual(job_info_data["job"]["id"], self.job.id)
        self.assertEqual(job_info_data["job"]["name"], "백엔드 개발자")
        self.assertEqual(job_info_data["job_category"]["id"], self.job_category.id)
        self.assertEqual(job_info_data["job_category"]["name"], "IT/개발")
        # write_only 필드는 응답에 포함되지 않음
        self.assertNotIn("job_id", job_info_data)
        self.assertNotIn("job_category_id", job_info_data)
        self.assertEqual(job_info_data["manual_job"], "")
        self.assertEqual(job_info_data["manual_job_category"], "")

    def test_serialize_profile_with_manual_job_info(self):
        """직접 입력 직업 / 직군 정보가 있는 프로필 직렬화 테스트"""
        # 기존 프로필 사용하고 JobInfo 수정
        profile = self.profile
        profile.mbti = Mbti.ENFP
        profile.gender = Gender.MALE
        profile.region = "대구"
        profile.city = "수성구"

        job_info = JobInfo.objects.create(
            job=None,
            job_category=None,
            manual_job="AI 개발자",
            manual_job_category="인공지능",
        )
        profile.job_info = job_info
        profile.save()

        # 직렬화
        serializer = MyProfileSerializer(profile)
        data = serializer.data

        # 검증
        self.assertEqual(data["mbti"], "ENFP")
        self.assertEqual(data["gender"], "M")
        self.assertEqual(data["region"], "대구")
        self.assertEqual(data["city"], "수성구")

        # JobInfo 검증
        job_info_data = data["job_info"]
        self.assertIsNotNone(job_info_data)
        self.assertIsNone(job_info_data["job"])
        self.assertIsNone(job_info_data["job_category"])
        self.assertEqual(job_info_data["manual_job"], "AI 개발자")
        self.assertEqual(job_info_data["manual_job_category"], "인공지능")
        # write_only 필드는 응답에 포함되지 않음
        self.assertNotIn("job_id", job_info_data)
        self.assertNotIn("job_category_id", job_info_data)

    def test_update_profile_basic_fields(self):
        """기본 필드 업데이트 테스트"""
        # 기존 프로필 사용
        profile = self.profile

        # 업데이트 데이터
        update_data = {
            "mbti": "ESTJ",
            "gender": "F",
            "region": "부산",
            "city": "해운대구",
            "introduction": "새로운 소개입니다.",
            "one_liner": "한 줄 소개",
            "tmi": "TMI 정보",
        }

        # 직렬화 및 업데이트
        serializer = MyProfileSerializer(profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()

        # 검증
        self.assertEqual(updated_profile.mbti, "ESTJ")
        self.assertEqual(updated_profile.gender, "F")
        self.assertEqual(updated_profile.region, "부산")
        self.assertEqual(updated_profile.city, "해운대구")
        self.assertEqual(updated_profile.introduction, "새로운 소개입니다.")
        self.assertEqual(updated_profile.one_liner, "한 줄 소개")
        self.assertEqual(updated_profile.tmi, "TMI 정보")

    def test_update_profile_with_job_selection(self):
        """직업 선택으로 업데이트 테스트"""
        # 기존 프로필 사용
        profile = self.profile

        # 업데이트 데이터 (직업 선택)
        update_data = {
            "mbti": "INTJ",
            "job_info": {
                "job_id": self.job.id,
                "job_category_id": self.job_category.id,
            },
        }

        # 직렬화 및 업데이트
        serializer = MyProfileSerializer(profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()

        # 검증
        self.assertEqual(updated_profile.mbti, "INTJ")
        self.assertIsNotNone(updated_profile.job_info)
        self.assertEqual(updated_profile.job_info.job, self.job)
        self.assertEqual(updated_profile.job_info.job_category, self.job_category)
        self.assertEqual(updated_profile.job_info.manual_job, "")
        self.assertEqual(updated_profile.job_info.manual_job_category, "")

    def test_update_profile_with_manual_job(self):
        """직접 직업 / 직군 입력으로 업데이트 테스트"""
        # 기존 프로필 사용
        profile = self.profile

        # 업데이트 데이터 (직업 / 직군)
        update_data = {
            "mbti": "ENFP",
            "job_info": {"manual_job": "AI 개발자", "manual_job_category": "인공지능"},
        }

        # 직렬화 및 업데이트
        serializer = MyProfileSerializer(profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()

        # 검증
        self.assertEqual(updated_profile.mbti, "ENFP")
        self.assertIsNotNone(updated_profile.job_info)
        self.assertIsNone(updated_profile.job_info.job)
        self.assertIsNone(updated_profile.job_info.job_category)
        self.assertEqual(updated_profile.job_info.manual_job, "AI 개발자")
        self.assertEqual(updated_profile.job_info.manual_job_category, "인공지능")

    def test_update_profile_existing_job_info(self):
        """기존 JobInfo가 있는 경우 업데이트 테스트"""
        # 기존 프로필 사용
        profile = self.profile

        job_info = JobInfo.objects.create(
            job=self.job,
            job_category=self.job_category,
            manual_job="",
            manual_job_category="",
        )
        profile.job_info = job_info
        profile.save()

        # 업데이트 데이터 (다른 직업으로 변경)
        update_data = {
            "job_info": {
                "job_id": self.other_job.id,
                "job_category_id": self.other_job_category.id,
            }
        }

        # 직렬화 및 업데이트
        serializer = MyProfileSerializer(profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()

        # 검증
        self.assertIsNotNone(updated_profile.job_info)
        self.assertEqual(updated_profile.job_info.job, self.other_job)
        self.assertEqual(updated_profile.job_info.job_category, self.other_job_category)
        self.assertEqual(updated_profile.job_info.manual_job, "")
        self.assertEqual(updated_profile.job_info.manual_job_category, "")

    def test_update_profile_no_job_info(self):
        """job_info 없이 업데이트 테스트"""
        # 프로필 생성
        profile = self.profile

        # 업데이트 데이터 (job_info를 None으로 설정)
        update_data = {
            "mbti": "ISFP",
            "gender": "F",
            "region": "대구",
            "city": "수성구",
            "job_info": None,
        }

        # 직렬화 및 업데이트
        serializer = MyProfileSerializer(profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()

        # 검증
        self.assertEqual(updated_profile.mbti, "ISFP")
        self.assertEqual(updated_profile.gender, "F")
        self.assertEqual(updated_profile.region, "대구")
        self.assertEqual(updated_profile.city, "수성구")
        self.assertIsNone(updated_profile.job_info)

    def test_update_profile_empty_job_info(self):
        """빈 job_info로 업데이트 테스트 - validation 오류 발생"""
        # 기존 프로필 사용
        profile = self.profile

        # 업데이트 데이터 (빈 job_info)
        update_data = {"mbti": "ENTP", "job_info": {}}

        # 직렬화 및 업데이트
        serializer = MyProfileSerializer(profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())  # serializer는 통과

        # 하지만 save() 시 모델 validation에서 오류 발생
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_serializer_with_none_job_info(self):
        """None job_info로 직렬화 테스트"""
        # 기존 프로필 사용하고 job_info를 None으로 설정
        profile = self.profile
        profile.job_info = None
        profile.save()

        # 직렬화
        serializer = MyProfileSerializer(profile)
        data = serializer.data

        # 검증
        self.assertEqual(data["mbti"], profile.mbti)  # 실제 프로필 값
        self.assertEqual(data["gender"], profile.gender)  # 실제 프로필 값
        self.assertIsNone(data["job_info"])

    def test_partial_update_preserves_existing_data(self):
        """부분 업데이트 시 기존 데이터 보존 테스트"""
        # 기존 프로필 사용
        profile = self.profile

        # 부분 업데이트 데이터 (mbti만 변경)
        update_data = {"mbti": "ESTP"}

        # 직렬화 및 업데이트
        serializer = MyProfileSerializer(profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()

        # 검증
        self.assertEqual(updated_profile.mbti, "ESTP")
        self.assertEqual(updated_profile.gender, profile.gender)
        self.assertEqual(updated_profile.region, profile.region)  # 기존 값 유지
        self.assertEqual(updated_profile.city, profile.city)  # 기존 값 유지
        self.assertEqual(updated_profile.introduction, profile.introduction)  # 기존 값 유지
