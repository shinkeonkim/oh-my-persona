from rest_framework import serializers

from matchmakings.models import ReferralOverallOpinion


class ReferralOverallOpinionSerializer(serializers.ModelSerializer):
  """추천 종합의견 시리얼라이저 (성별에 따라 적절한 의견 반환)"""

  referred_algorithm = serializers.CharField(source='referral.referred_algorithm', read_only=True)
  overall_opinion = serializers.SerializerMethodField()

  class Meta:
    model = ReferralOverallOpinion
    fields = [
      "id",
      "overall_opinion",
      "generation_status",
      "referred_algorithm",
      "created_at",
      "updated_at",
    ]
    read_only_fields = [
      "id",
      "overall_opinion",
      "generation_status",
      "referred_algorithm",
      "created_at",
      "updated_at",
    ]

  def get_overall_opinion(self, obj):
    """사용자의 성별에 따라 적절한 의견 반환"""
    request = self.context.get("request")
    if not request or not hasattr(request, "user"):
      return ""

    user_gender = request.user.profile.gender if hasattr(request.user, "profile") else None

    if user_gender == "M":
      return obj.opinion_for_male
    elif user_gender == "F":
      return obj.opinion_for_female
    return ""
