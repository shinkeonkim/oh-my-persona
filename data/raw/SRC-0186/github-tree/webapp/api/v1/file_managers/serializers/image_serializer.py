from django.conf import settings

from rest_framework import serializers

from file_managers.models import Image


class ImageSerializer(serializers.ModelSerializer):
  file = serializers.SerializerMethodField()

  def get_file(self, obj):
    BASE_URL = settings.BASE_URL.rstrip("/")
    file_url = obj.file.url

    return f"{BASE_URL}{file_url}"

  class Meta:
    model = Image
    fields = (
      "id",
      "file",
      "created_at",
      "updated_at",
    )
    read_only_fields = (
      "id",
      "created_at",
      "updated_at",
    )
