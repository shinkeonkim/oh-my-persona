from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from common.choices import Gender, Mbti
from profiles.factories import JobCategoryFactory, JobFactory, JobInfoFactory
from users.factories import UserFactory


class MyProfileViewTestCase(TestCase):
    """MyProfileView 테스트 케이스"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()

        self.job_category = JobCategoryFactory(name="IT/개발")
        self.job = JobFactory(name="백엔드 개발자", job_category=self.job_category)
        self.other_job_category = JobCategoryFactory(name="디자인")
        self.other_job = JobFactory(name="UI/UX 디자이너", job_category=self.other_job_category)

        # Factory를 사용한 테스트 데이터 생성 (확인하지 않고 생성)
        self.user = UserFactory(
            email="test@example.com",
            username="testuser",
            real_name="테스트 사용자",
            phone_number="010-1234-5678",
            confirm_user=False,  # 나중에 수동으로 확인
        )
        # UserFactory에서 이미 profile을 생성했으므로, 기존 profile을 사용
        self.profile = self.user.profile
        # JobInfo 추가
        from profiles.factories import JobInfoFactory

        self.profile.job_info = JobInfoFactory(job=self.job, job_category=self.job_category)
        self.profile.save()

        # 사용자 확인 처리
        self.user.confirm()

    def test_get_profile_success(self):
        """프로필 조회 성공 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.get(url)

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("mbti", response.data)
        self.assertIn("job_info", response.data)
        # job_info가 생성되었는지 확인
        self.assertIsNotNone(response.data["job_info"])

    def test_get_profile_with_existing_data(self):
        """기존 데이터가 있는 프로필 조회 테스트"""
        # 기존 프로필 사용하고 JobInfo 추가
        self.profile = self.user.profile
        self.profile.mbti = Mbti.INFP
        self.profile.gender = Gender.MALE
        self.profile.region = "서울"
        self.profile.city = "강남구"
        self.profile.introduction = "안녕하세요! 개발자입니다."
        self.profile.job_info = JobInfoFactory(
            job=self.job,
            job_category=self.job_category,
            manual_job="",
            manual_job_category="",
        )
        self.profile.save()

        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.get(url)

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mbti"], "INFP")
        self.assertEqual(response.data["gender"], "M")
        self.assertEqual(response.data["region"], "서울")
        self.assertEqual(response.data["city"], "강남구")
        self.assertEqual(response.data["introduction"], "안녕하세요! 개발자입니다.")

        # JobInfo 확인
        job_info_data = response.data["job_info"]
        self.assertIsNotNone(job_info_data)
        self.assertEqual(job_info_data["job"]["id"], self.job.id)
        self.assertEqual(job_info_data["job"]["name"], "백엔드 개발자")
        self.assertEqual(job_info_data["job_category"]["id"], self.job_category.id)
        self.assertEqual(job_info_data["job_category"]["name"], "IT/개발")
        # job_id와 job_category_id는 write_only이므로 응답에 포함되지 않음

    def test_update_profile_basic_fields(self):
        """기본 필드 업데이트 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터
        update_data = {
            "mbti": "ESTJ",
            "gender": "F",
            "region": "부산",
            "city": "해운대구",
            "introduction": "안녕하세요! 새로운 소개입니다.",
            "one_liner": "한 줄 소개",
            "tmi": "TMI 정보입니다.",
        }

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mbti"], "ESTJ")
        self.assertEqual(response.data["gender"], "F")
        self.assertEqual(response.data["region"], "부산")
        self.assertEqual(response.data["city"], "해운대구")
        self.assertEqual(response.data["introduction"], "안녕하세요! 새로운 소개입니다.")
        self.assertEqual(response.data["one_liner"], "한 줄 소개")
        self.assertEqual(response.data["tmi"], "TMI 정보입니다.")

    def test_update_profile_with_job_selection(self):
        """직업 선택으로 업데이트 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (직업 선택)
        update_data = {
            "mbti": "INTJ",
            "jobInfo": {"jobId": self.job.id, "jobCategoryId": self.job_category.id},
        }

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mbti"], "INTJ")

        # JobInfo 확인
        job_info_data = response.data["job_info"]
        self.assertIsNotNone(job_info_data)
        self.assertEqual(job_info_data["job"]["id"], self.job.id)
        self.assertEqual(job_info_data["job"]["name"], "백엔드 개발자")
        self.assertEqual(job_info_data["job_category"]["id"], self.job_category.id)
        self.assertEqual(job_info_data["job_category"]["name"], "IT/개발")
        # job_id와 job_category_id는 write_only이므로 응답에 포함되지 않음
        self.assertEqual(job_info_data["manual_job"], "")
        self.assertEqual(job_info_data["manual_job_category"], "")

    def test_update_profile_with_manual_job(self):
        """직접 직업/직군 입력으로 업데이트 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (직접 입력 직업 / 직군)
        update_data = {
            "mbti": "ENFP",
            "jobInfo": {"manualJob": "AI 개발자", "manualJobCategory": "인공지능"},
        }

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mbti"], "ENFP")

        # JobInfo 확인
        job_info_data = response.data["job_info"]
        self.assertIsNotNone(job_info_data)
        self.assertIsNone(job_info_data["job"])
        self.assertIsNone(job_info_data["job_category"])
        self.assertEqual(job_info_data["manual_job"], "AI 개발자")
        self.assertEqual(job_info_data["manual_job_category"], "인공지능")

    def test_update_profile_job_info_existing(self):
        """기존 JobInfo가 있는 경우 업데이트 테스트"""
        # 기존 프로필 사용하고 JobInfo 추가
        self.profile = self.user.profile
        self.profile.mbti = Mbti.INFP
        self.profile.job_info = JobInfoFactory(
            job=self.job,
            job_category=self.job_category,
            manual_job="",
            manual_job_category="",
        )
        self.profile.save()

        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (다른 직업으로 변경)
        update_data = {
            "jobInfo": {
                "jobId": self.other_job.id,
                "jobCategoryId": self.other_job_category.id,
            }
        }

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # JobInfo 확인
        job_info_data = response.data["job_info"]
        self.assertEqual(job_info_data["job"]["id"], self.other_job.id)
        self.assertEqual(job_info_data["job"]["name"], "UI/UX 디자이너")
        self.assertEqual(job_info_data["job_category"]["id"], self.other_job_category.id)
        self.assertEqual(job_info_data["job_category"]["name"], "디자인")

    def test_update_profile_invalid_job_id(self):
        """잘못된 job_id로 업데이트 시 오류 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (존재하지 않는 job_id)
        update_data = {
            "jobInfo": {
                "jobId": 99999,  # 존재하지 않는 ID
                "jobCategoryId": self.job_category.id,
            }
        }

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("details", response.data)
        self.assertIn("job_info", response.data["details"])
        self.assertIn("job_id", response.data["details"]["job_info"])

    def test_update_profile_invalid_job_category_id(self):
        """잘못된 job_category_id로 업데이트 시 오류 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (존재하지 않는 job_category_id)
        update_data = {
            "jobInfo": {
                "jobId": self.job.id,
                "jobCategoryId": 99999,  # 존재하지 않는 ID
            }
        }

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("details", response.data)
        self.assertIn("job_info", response.data["details"])
        self.assertIn("job_category_id", response.data["details"]["job_info"])

    def test_update_profile_job_category_mismatch(self):
        """job과 job_category가 일치하지 않는 경우 오류 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (job과 job_category가 다른 카테고리)
        update_data = {
            "jobInfo": {
                "jobId": self.job.id,  # IT/개발 카테고리의 직업
                "jobCategoryId": self.other_job_category.id,  # 디자인 카테고리
            }
        }

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_update_profile_mixed_job_and_manual(self):
        """job 선택과 직접 입력을 동시에 하는 경우 오류 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (job 선택과 직접 입력 동시)
        update_data = {
            "jobInfo": {
                "jobId": self.job.id,
                "jobCategoryId": self.job_category.id,
                "manualJob": "직접 입력 직업",
                "manualJobCategory": "직접 입력 직군",
            }
        }

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_update_profile_no_job_info(self):
        """job_info 없이 업데이트 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (job_info를 None으로 설정)
        update_data = {
            "mbti": "ISFP",
            "gender": "M",
            "region": "대구",
            "city": "수성구",
            "job_info": None,
        }

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mbti"], "ISFP")
        self.assertEqual(response.data["gender"], "M")
        self.assertEqual(response.data["region"], "대구")
        self.assertEqual(response.data["city"], "수성구")
        self.assertIsNone(response.data["job_info"])

    def test_update_profile_empty_job_info(self):
        """빈 job_info로 업데이트 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (빈 job_info)
        update_data = {"mbti": "ENTP", "jobInfo": {}}

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인 (validation 오류 예상)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_unauthorized_access(self):
        """인증되지 않은 접근 테스트"""
        # API 호출 (인증 없이)
        url = "/api/v1/profiles/me/"
        response = self.client.get(url)

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update(self):
        """부분 업데이트 테스트"""
        # 기존 프로필 사용
        profile = self.user.profile

        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 부분 업데이트 데이터 (mbti만 변경)
        update_data = {"mbti": "ESTP"}

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mbti"], "ESTP")
        self.assertEqual(response.data["gender"], profile.gender)  # 기존 값 유지
        self.assertEqual(response.data["region"], profile.region)  # 기존 값 유지
        self.assertEqual(response.data["city"], profile.city)  # 기존 값 유지

    def test_job_info_validation_errors(self):
        """JobInfo validation 오류 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (job과 manual_job 모두 없음)
        update_data = {"jobInfo": {"jobCategoryId": self.job_category.id}}

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인 - job_category만 있고 job이 없으면 validation 오류 발생
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 응답 데이터 확인
        response_data = response.json()
        self.assertIn("message", response_data)
        self.assertIn("직업을 선택하거나 수동으로 입력해야 합니다.", response_data["message"])

    def test_job_info_manual_job_category_validation(self):
        """JobInfo 직접 입력 직군 validation 테스트"""
        # 인증 설정
        self.client.force_authenticate(user=self.user)

        # 업데이트 데이터 (manual_job만 있고 manual_job_category 없음)
        update_data = {"jobInfo": {"manualJob": "개발자"}}

        # API 호출
        url = "/api/v1/profiles/me/"
        response = self.client.patch(url, data=update_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
