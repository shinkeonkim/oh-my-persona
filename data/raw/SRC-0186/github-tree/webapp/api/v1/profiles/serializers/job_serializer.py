from rest_framework import serializers

from profiles.models.job import Job


class JobSerializer(serializers.ModelSerializer):
    job_category_name = serializers.CharField(source="job_category.name", read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "name",
            "job_category",
            "job_category_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "job_category_name", "created_at", "updated_at"]
