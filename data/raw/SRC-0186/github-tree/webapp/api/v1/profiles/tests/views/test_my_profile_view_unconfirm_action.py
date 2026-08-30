from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from common.choices import BirthTime, Gender, Mbti
from profiles.factories import JobCategoryFactory, JobFactory, JobInfoFactory
from users.factories import UserFactory


class MyProfileViewUnconfirmActionTestCase(TestCase):
  """MyProfileView 온보딩 필드 변경 시 unconfirm 동작 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.client = APIClient()

    # Job 관련 데이터
    self.job_category = JobCategoryFactory(name="IT/개발")
    self.job = JobFactory(name="백엔드 개발자", job_category=self.job_category)
    self.other_job_category = JobCategoryFactory(name="디자인")
    self.other_job = JobFactory(name="UI/UX 디자이너", job_category=self.other_job_category)

    # 확인된 사용자 생성
    self.user = UserFactory(
      email="test@example.com",
      username="testuser",
      real_name="테스트 사용자",
      phone_number="010-1234-5678",
      confirm_user=False,
    )

    # 프로필 초기 설정
    self.profile = self.user.profile
    self.profile.mbti = Mbti.INFP
    self.profile.gender = Gender.MALE
    self.profile.region = "서울"
    self.profile.city = "강남구"
    self.profile.birth_time = BirthTime.JASHI
    self.profile.introduction = "안녕하세요!"
    self.profile.one_liner = "개발자입니다"
    self.profile.tmi = "커피를 좋아합니다"
    self.profile.job_info = JobInfoFactory(
      job=self.job,
      job_category=self.job_category,
    )
    self.profile.save()

    # 사용자 확인 처리
    self.user.confirm()

  def test_update_birth_time_should_unconfirm(self):
    """birth_time 변경 시 unconfirm 되어야 함"""
    # 인증 설정
    self.client.force_authenticate(user=self.user)

    # 사용자가 확인된 상태인지 확인
    self.assertTrue(self.user.is_confirmed)

    # birth_time 업데이트
    update_data = {"birth_time": BirthTime.CHUKSHI}

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    # 응답 확인
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["birth_time"], BirthTime.CHUKSHI)

    # 사용자 재조회하여 unconfirm 되었는지 확인
    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)

  def test_update_mbti_should_unconfirm(self):
    """mbti 변경 시 unconfirm 되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {"mbti": Mbti.ESTJ}

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["mbti"], Mbti.ESTJ)

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)

  def test_update_region_should_unconfirm(self):
    """region 변경 시 unconfirm 되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {"region": "부산"}

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["region"], "부산")

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)

  def test_update_city_should_unconfirm(self):
    """city 변경 시 unconfirm 되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {"city": "해운대구"}

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["city"], "해운대구")

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)

  def test_update_job_id_should_unconfirm(self):
    """job_id 변경 시 unconfirm 되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {
      "job_info": {
        "job_id": self.other_job.id,
        "job_category_id": self.other_job_category.id,
      }
    }

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["job_info"]["job"]["id"], self.other_job.id)

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)

  def test_update_job_category_id_should_unconfirm(self):
    """job_category_id 변경 시 unconfirm 되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    # 같은 카테고리 내 다른 직업으로 변경
    another_job = JobFactory(name="프론트엔드 개발자", job_category=self.other_job_category)

    update_data = {
      "job_info": {
        "job_id": another_job.id,
        "job_category_id": self.other_job_category.id,
      }
    }

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["job_info"]["job_category"]["id"], self.other_job_category.id)

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)

  def test_update_to_different_job_info_should_unconfirm(self):
    """다른 job_info로 변경 시 unconfirm 되어야 함"""
    # 이미 setUp에서 job_info가 설정되어 confirm된 상태
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    # 완전히 다른 job으로 변경
    update_data = {
      "job_info": {
        "job_id": self.other_job.id,
        "job_category_id": self.other_job_category.id,
      }
    }

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["job_info"]["job"]["id"], self.other_job.id)

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)

  def test_update_manual_job_should_unconfirm(self):
    """manual_job 변경 시 unconfirm 되어야 함"""
    # setUp에서 이미 job과 job_category가 있는 상태에서 manual_job만 추가로 변경
    # (is_intro_completed는 job과 job_category를 필요로 하므로 그대로 유지)
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    # JobInfo 업데이트를 통해 manual_job 변경 테스트
    update_data = {
      "job_info": {
        "manual_job": "AI 개발자",
        "manual_job_category": "인공지능",
      }
    }

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    # manual_job이 설정되었는지 확인
    self.assertEqual(response.data["job_info"]["manual_job"], "AI 개발자")

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)

  def test_update_manual_job_category_should_unconfirm(self):
    """manual_job_category 변경 시 unconfirm 되어야 함"""
    # setUp에서 이미 확인된 상태
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    # manual_job_category만 변경
    update_data = {
      "job_info": {
        "manual_job": "개발자",
        "manual_job_category": "소프트웨어",
      }
    }

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["job_info"]["manual_job_category"], "소프트웨어")

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)

  def test_update_multiple_onboarding_fields_should_unconfirm_once(self):
    """여러 온보딩 필드 동시 변경 시 한 번만 unconfirm 되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {
      "mbti": Mbti.ENTP,
      "region": "인천",
      "city": "남동구",
      "birth_time": BirthTime.INSHI,
    }

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)

  # 온보딩 필드가 아닌 필드 변경 시 승인 상태 유지 테스트

  def test_update_introduction_should_not_unconfirm(self):
    """introduction 변경 시 승인 상태 유지되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {"introduction": "새로운 소개입니다!"}

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["introduction"], "새로운 소개입니다!")

    self.user.refresh_from_db()
    self.assertTrue(self.user.is_confirmed)  # 여전히 확인된 상태

  def test_update_one_liner_should_not_unconfirm(self):
    """one_liner 변경 시 승인 상태 유지되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {"one_liner": "새로운 한줄소개"}

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["one_liner"], "새로운 한줄소개")

    self.user.refresh_from_db()
    self.assertTrue(self.user.is_confirmed)

  def test_update_tmi_should_not_unconfirm(self):
    """tmi 변경 시 승인 상태 유지되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {"tmi": "새로운 TMI 정보"}

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["tmi"], "새로운 TMI 정보")

    self.user.refresh_from_db()
    self.assertTrue(self.user.is_confirmed)

  def test_update_gender_should_not_unconfirm(self):
    """gender 변경 시 승인 상태 유지되어야 함 (온보딩 필드 아님)"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {"gender": Gender.FEMALE}

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["gender"], Gender.FEMALE)

    self.user.refresh_from_db()
    self.assertTrue(self.user.is_confirmed)

  def test_update_multiple_non_onboarding_fields_should_not_unconfirm(self):
    """여러 비온보딩 필드 동시 변경 시 승인 상태 유지되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {
      "introduction": "완전 새로운 소개",
      "one_liner": "완전 새로운 한줄소개",
      "tmi": "완전 새로운 TMI",
      "gender": Gender.FEMALE,
    }

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    self.user.refresh_from_db()
    self.assertTrue(self.user.is_confirmed)  # 여전히 확인된 상태

  def test_update_mixed_onboarding_and_non_onboarding_should_unconfirm(self):
    """온보딩 필드와 비온보딩 필드 동시 변경 시 unconfirm 되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    update_data = {
      "mbti": Mbti.ISFJ,  # 온보딩 필드
      "introduction": "새로운 소개",  # 비온보딩 필드
      "one_liner": "새로운 한줄소개",  # 비온보딩 필드
    }

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["mbti"], Mbti.ISFJ)
    self.assertEqual(response.data["introduction"], "새로운 소개")

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)  # unconfirm 됨

  def test_update_same_value_should_not_unconfirm(self):
    """같은 값으로 업데이트 시 승인 상태 유지되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    # 현재 값과 동일한 값으로 업데이트
    update_data = {
      "mbti": Mbti.INFP,  # 기존 값과 동일
      "region": "서울",  # 기존 값과 동일
    }

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    self.user.refresh_from_db()
    self.assertTrue(self.user.is_confirmed)  # 변경 사항 없으므로 확인 상태 유지

  def test_unconfirmed_user_update_should_remain_unconfirmed(self):
    """이미 미확인 상태인 사용자가 온보딩 필드 변경 시 미확인 상태 유지"""
    # 사용자를 미확인 상태로 만듦
    self.user.unconfirm()
    self.assertFalse(self.user.is_confirmed)

    self.client.force_authenticate(user=self.user)

    update_data = {"mbti": Mbti.ESTP}

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    self.user.refresh_from_db()
    self.assertFalse(self.user.is_confirmed)  # 여전히 미확인 상태

  def test_update_job_info_with_same_values_should_not_unconfirm(self):
    """job_info를 같은 값으로 업데이트 시 승인 상태 유지되어야 함"""
    self.client.force_authenticate(user=self.user)
    self.assertTrue(self.user.is_confirmed)

    # 현재 job_info와 동일한 값으로 업데이트
    update_data = {
      "job_info": {
        "job_id": self.job.id,
        "job_category_id": self.job_category.id,
      }
    }

    url = "/api/v1/profiles/me/"
    response = self.client.patch(url, data=update_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    self.user.refresh_from_db()
    self.assertTrue(self.user.is_confirmed)  # 변경 사항 없으므로 확인 상태 유지
