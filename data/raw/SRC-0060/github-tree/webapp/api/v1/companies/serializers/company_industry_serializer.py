from rest_framework import serializers

from companies.models import CompanyIndustry


class IndustrySerializer(serializers.ModelSerializer):

  class Meta:
    model = CompanyIndustry
    fields = ["name"]
