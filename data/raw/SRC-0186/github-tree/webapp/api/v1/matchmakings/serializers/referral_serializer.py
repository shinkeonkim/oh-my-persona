from rest_framework import serializers

from api.v1.profiles.serializers.user_profile_serializer import UserProfileSerializer
from matchmakings.models import Referral


class ReferralSerializer(serializers.ModelSerializer):
  """Referral 상세 정보 시리얼라이저"""
  user = UserProfileSerializer(read_only=True)
  referral_user = UserProfileSerializer(read_only=True)
  conversation = serializers.SerializerMethodField(help_text="추천 대화 정보", )

  def get_conversation(self, obj):
    conversation = getattr(obj, 'conversation', None)

    if not conversation:
      return []

    request = self.context.get('request')

    if not request or not request.user:
      return []

    current_user = request.user

    if current_user == obj.user:
      return conversation.conversation_messages or []
    elif current_user == obj.referral_user:
      return conversation.opposite_conversation_messages or []

    return []

  class Meta:
    model = Referral
    fields = [
      "id",
      "user",
      "referral_user",
      "conversation",
      "referred_at",
      "created_at",
      "updated_at",
    ]
    read_only_fields = [
      "id",
      "user",
      "referral_user",
      "conversation",
      "referred_at",
      "created_at",
      "updated_at",
    ]
