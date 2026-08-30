from rest_framework import serializers


class ReferralResetQuotaResponseSerializer(serializers.Serializer):
    """추천 횟수 초기화 응답 시리얼라이저"""

    message = serializers.CharField(help_text="응답 메시지")
    remaining_referral_quota = serializers.IntegerField(help_text="초기화된 추천 횟수")
    ticket_amount = serializers.IntegerField(help_text="남은 티켓 개수")
    used_tickets = serializers.IntegerField(help_text="사용된 티켓 개수")
