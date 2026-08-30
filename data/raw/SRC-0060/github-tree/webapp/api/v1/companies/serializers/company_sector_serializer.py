from rest_framework import serializers

from companies.models import CompanySector


class CompanySectorSerializer(serializers.ModelSerializer):

  class Meta:
    model = CompanySector
    fields = ["name"]
