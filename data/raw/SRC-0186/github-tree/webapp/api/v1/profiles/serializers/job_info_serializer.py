from rest_framework import serializers

from profiles.models import Job, JobCategory, JobInfo

from .job_category_serializer import JobCategorySerializer
from .job_serializer import JobSerializer


class JobInfoSerializer(serializers.ModelSerializer):
    """직업 정보 시리얼라이저"""

    job = JobSerializer(read_only=True)
    job_category = JobCategorySerializer(read_only=True)

    job_id = serializers.IntegerField(
        allow_null=True,
        required=False,
        write_only=True,
        help_text="선택된 직업 ID (입력용)",
    )

    job_category_id = serializers.IntegerField(
        allow_null=True,
        required=False,
        write_only=True,
        help_text="선택된 직군 ID (입력용)",
    )

    manual_job = serializers.CharField(max_length=100, allow_blank=True, required=False, help_text="직접 입력 직업명")

    manual_job_category = serializers.CharField(
        max_length=100, allow_blank=True, required=False, help_text="직접 입력 직군"
    )

    class Meta:
        model = JobInfo
        fields = [
            "job",
            "job_category",
            "job_id",
            "job_category_id",
            "manual_job",
            "manual_job_category",
        ]
        read_only_fields = [
            "job",
            "job_category",
        ]

        write_only_fields = [
            "job_id",
            "job_category_id",
        ]

    def _process_job_data(self, validated_data):
        """job_id와 job_category_id를 실제 객체로 변환하는 공통 메서드"""
        job_id = validated_data.pop("job_id", None)
        job_category_id = validated_data.pop("job_category_id", None)

        if job_id:
            try:
                validated_data["job"] = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                raise serializers.ValidationError({"job_id": "해당 직업을 찾을 수 없습니다."})

        if job_category_id:
            try:
                validated_data["job_category"] = JobCategory.objects.get(id=job_category_id)
            except JobCategory.DoesNotExist:
                raise serializers.ValidationError({"job_category_id": "해당 직군을 찾을 수 없습니다."})

    def create(self, validated_data):
        """JobInfo 생성"""
        self._process_job_data(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """JobInfo 업데이트"""
        self._process_job_data(validated_data)
        return super().update(instance, validated_data)
