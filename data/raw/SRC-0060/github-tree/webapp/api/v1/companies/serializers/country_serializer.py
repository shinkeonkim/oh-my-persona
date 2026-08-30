from rest_framework import serializers

from companies.models import Country


class CountrySerializer(serializers.ModelSerializer):

  class Meta:
    model = Country
    fields = ["code", "name"]
