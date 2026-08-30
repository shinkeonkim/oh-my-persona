from django.core.exceptions import ValidationError
from django.test import TestCase

from api.v1.profiles.serializers.job_info_serializer import JobInfoSerializer
from profiles.factories import JobCategoryFactory, JobFactory, JobInfoFactory
from profiles.models import JobInfo


class JobInfoSerializerTestCase(TestCase):
    """JobInfoSerializer 테스트 케이스"""

    def setUp(self):
        """테스트 데이터 설정"""
        # Factory를 사용한 테스트 데이터 생성
        self.job_category = JobCategoryFactory(name="IT/개발")
        self.job = JobFactory(name="백엔드 개발자", job_category=self.job_category)
        self.other_job_category = JobCategoryFactory(name="디자인")
        self.other_job = JobFactory(name="UI/UX 디자이너", job_category=self.other_job_category)

    def test_serializer_creation(self):
        """Serializer 생성 테스트"""
        serializer = JobInfoSerializer()
        self.assertIsInstance(serializer, JobInfoSerializer)

    def test_serializer_fields(self):
        """Serializer 필드 확인 테스트"""
        serializer = JobInfoSerializer()
        expected_fields = [
            "job",
            "job_category",
            "job_id",
            "job_category_id",
            "manual_job",
            "manual_job_category",
        ]

        for field in expected_fields:
            self.assertIn(field, serializer.fields)

    def test_serializer_read_only_fields(self):
        """Serializer read_only 필드 확인 테스트"""
        serializer = JobInfoSerializer()
        read_only_fields = ["job", "job_category"]

        for field in read_only_fields:
            self.assertTrue(serializer.fields[field].read_only)

    def test_serializer_write_only_fields(self):
        """Serializer write_only 필드 확인 테스트"""
        serializer = JobInfoSerializer()
        write_only_fields = ["job_id", "job_category_id"]

        for field in write_only_fields:
            self.assertTrue(serializer.fields[field].write_only)

    def test_serialize_job_info_with_job_selection(self):
        """직업 선택이 있는 JobInfo 직렬화 테스트"""
        # Factory를 사용하여 JobInfo 생성
        job_info = JobInfoFactory(
            job=self.job,
            job_category=self.job_category,
            manual_job="",
            manual_job_category="",
        )

        # 직렬화
        serializer = JobInfoSerializer(job_info)
        data = serializer.data

        # 검증
        self.assertIsNotNone(data["job"])
        self.assertEqual(data["job"]["id"], self.job.id)
        self.assertEqual(data["job"]["name"], "백엔드 개발자")
        self.assertEqual(data["job"]["job_category"], self.job_category.id)
        self.assertEqual(data["job"]["job_category_name"], "IT/개발")

        self.assertIsNotNone(data["job_category"])
        self.assertEqual(data["job_category"]["id"], self.job_category.id)
        self.assertEqual(data["job_category"]["name"], "IT/개발")

        # write_only 필드는 응답에 포함되지 않음
        self.assertNotIn("job_id", data)
        self.assertNotIn("job_category_id", data)
        self.assertEqual(data["manual_job"], "")
        self.assertEqual(data["manual_job_category"], "")

    def test_serialize_job_info_with_manual_job(self):
        """직접 입력 정보가 있는 JobInfo 직렬화 테스트"""
        job_info = JobInfoFactory(
            job=None,
            job_category=None,
            manual_job="AI 개발자",
            manual_job_category="인공지능",
        )

        # 직렬화
        serializer = JobInfoSerializer(job_info)
        data = serializer.data

        # 검증
        self.assertIsNone(data["job"])
        self.assertIsNone(data["job_category"])
        # write_only 필드는 응답에 포함되지 않음
        self.assertNotIn("job_id", data)
        self.assertNotIn("job_category_id", data)
        self.assertEqual(data["manual_job"], "AI 개발자")
        self.assertEqual(data["manual_job_category"], "인공지능")

    def test_serialize_job_info_empty(self):
        """빈 JobInfo 직렬화 테스트 - validation 오류 발생"""
        # JobInfo 생성 시 validation 오류 발생
        with self.assertRaises(ValidationError):
            JobInfo.objects.create(job=None, job_category=None, manual_job="", manual_job_category="")

    def test_create_job_info_with_job_selection(self):
        """직업 선택으로 JobInfo 생성 테스트"""
        # 생성 데이터
        create_data = {
            "job_id": self.job.id,
            "job_category_id": self.job_category.id,
            "manual_job": "",
            "manual_job_category": "",
        }

        # 직렬화 및 생성
        serializer = JobInfoSerializer(data=create_data)
        self.assertTrue(serializer.is_valid())
        job_info = serializer.save()

        # 검증
        self.assertEqual(job_info.job, self.job)
        self.assertEqual(job_info.job_category, self.job_category)
        self.assertEqual(job_info.manual_job, "")
        self.assertEqual(job_info.manual_job_category, "")

    def test_create_job_info_with_manual_job(self):
        """직접 입력 정보가 있는 JobInfo 생성 테스트"""
        # 생성 데이터
        create_data = {
            "job_id": None,
            "job_category_id": None,
            "manual_job": "AI 개발자",
            "manual_job_category": "인공지능",
        }

        # 직렬화 및 생성
        serializer = JobInfoSerializer(data=create_data)
        self.assertTrue(serializer.is_valid())
        job_info = serializer.save()

        # 검증
        self.assertIsNone(job_info.job)
        self.assertIsNone(job_info.job_category)
        self.assertEqual(job_info.manual_job, "AI 개발자")
        self.assertEqual(job_info.manual_job_category, "인공지능")

    def test_create_job_info_empty(self):
        """빈 JobInfo 생성 테스트 - validation 오류 발생"""
        # 생성 데이터 (모든 필드가 비어있음)
        create_data = {
            "job_id": None,
            "job_category_id": None,
            "manual_job": "",
            "manual_job_category": "",
        }

        # 직렬화 및 생성 (validation 오류 발생)
        serializer = JobInfoSerializer(data=create_data)
        self.assertTrue(serializer.is_valid())  # serializer는 통과

        # 하지만 save() 시 모델 validation에서 오류 발생
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_update_job_info_with_job_selection(self):
        """직업 선택으로 JobInfo 업데이트 테스트"""
        # Factory를 사용하여 기존 JobInfo 생성
        job_info = JobInfoFactory(
            job=None,
            job_category=None,
            manual_job="기존 직접 입력 직업",
            manual_job_category="기존 직접 입력 직군",
        )

        # 업데이트 데이터
        update_data = {
            "job_id": self.job.id,
            "job_category_id": self.job_category.id,
            "manual_job": "",
            "manual_job_category": "",
        }

        # 직렬화 및 업데이트
        serializer = JobInfoSerializer(job_info, data=update_data)
        self.assertTrue(serializer.is_valid())
        updated_job_info = serializer.save()

        # 검증
        self.assertEqual(updated_job_info.job, self.job)
        self.assertEqual(updated_job_info.job_category, self.job_category)
        self.assertEqual(updated_job_info.manual_job, "")
        self.assertEqual(updated_job_info.manual_job_category, "")

    def test_update_job_info_with_manual_job(self):
        """직접 입력 정보가 있는 JobInfo 업데이트 테스트 - validation 오류 발생"""
        # Factory를 사용하여 기존 JobInfo 생성 (job이 있는 상태)
        job_info = JobInfoFactory(
            job=self.job,
            job_category=self.job_category,
            manual_job="",
            manual_job_category="",
        )

        # 업데이트 데이터 (job이 있는 상태에서 manual_job으로 변경 시도)
        update_data = {
            "job_id": None,
            "job_category_id": None,
            "manual_job": "새로운 직접 입력 직업",
            "manual_job_category": "새로운 직접 입력 직군",
        }

        # 직렬화 및 업데이트
        serializer = JobInfoSerializer(job_info, data=update_data)
        self.assertTrue(serializer.is_valid())  # serializer는 통과

        # 하지만 save() 시 모델 validation에서 오류 발생
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_serializer_with_partial_data(self):
        """부분 데이터로 직렬화 테스트"""
        # Factory를 사용하여 JobInfo 생성
        job_info = JobInfoFactory(
            job=self.job,
            job_category=self.job_category,
            manual_job="",
            manual_job_category="",
        )

        # 직렬화
        serializer = JobInfoSerializer(job_info)
        data = serializer.data

        # 검증 - 모든 필드가 포함되어야 함
        self.assertIn("job", data)
        self.assertIn("job_category", data)
        self.assertIn("manual_job", data)
        self.assertIn("manual_job_category", data)
        # write_only 필드는 응답에 포함되지 않음
        self.assertNotIn("job_id", data)
        self.assertNotIn("job_category_id", data)

    def test_serializer_field_help_text(self):
        """Serializer 필드 help_text 확인 테스트"""
        serializer = JobInfoSerializer()

        # help_text 확인
        self.assertEqual(serializer.fields["job_id"].help_text, "선택된 직업 ID (입력용)")
        self.assertEqual(serializer.fields["job_category_id"].help_text, "선택된 직군 ID (입력용)")
        self.assertEqual(serializer.fields["manual_job"].help_text, "직접 입력 직업명")
        self.assertEqual(serializer.fields["manual_job_category"].help_text, "직접 입력 직군")

    def test_serializer_meta_fields(self):
        """Serializer Meta fields 확인 테스트"""
        serializer = JobInfoSerializer()
        expected_fields = [
            "job",
            "job_category",
            "job_id",
            "job_category_id",
            "manual_job",
            "manual_job_category",
        ]

        self.assertEqual(serializer.Meta.fields, expected_fields)

    def test_serializer_meta_read_only_fields(self):
        """Serializer Meta read_only_fields 확인 테스트"""
        serializer = JobInfoSerializer()
        expected_read_only_fields = ["job", "job_category"]

        self.assertEqual(serializer.Meta.read_only_fields, expected_read_only_fields)

    def test_serializer_meta_write_only_fields(self):
        """Serializer Meta write_only_fields 확인 테스트"""
        serializer = JobInfoSerializer()
        expected_write_only_fields = ["job_id", "job_category_id"]

        self.assertEqual(serializer.Meta.write_only_fields, expected_write_only_fields)
