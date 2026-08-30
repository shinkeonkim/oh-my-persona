from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError as DjangoIntegrityError
from django.db import transaction
from django.utils import timezone

from api.v1.matchmakings.exceptions import ReferralNotFoundError
from common.exceptions.custom_exceptions import ValidationError
from common.utils.logger import get_logger
from matchmakings.models import Matching, Referral
from users.services.ticket_service import TicketService

User = get_user_model()
logger = get_logger(__name__)


class MatchingCreationService:
  """매칭 생성 관련 서비스"""

  @staticmethod
  @transaction.atomic
  def create_matching_from_referral(user, referral_id, ticket_amount=None):
    """추천으로부터 매칭 생성"""
    try:
      # 추천 조회
      referral = Referral.objects.select_related("referral_user").get(id=referral_id, user=user)

      # 사용할 티켓 수량 결정
      if ticket_amount is None:
        ticket_amount = settings.MATCHING_TICKET_COST

      # 매칭 생성
      matching = Matching.objects.create(
        sender=user,
        receiver=referral.referral_user,
        ticket_amount=ticket_amount,
        sent_at=timezone.now(),
        referral=referral,
      )

      # 티켓 차감
      TicketService(user).use_tickets(
        amount=ticket_amount,
        description=f"매칭 생성 - {referral.referral_user.username}에게 호감 전송",
        matching=matching,
      )

      return matching

    except Referral.DoesNotExist:
      raise ReferralNotFoundError(message="Referral not found", details={"referral_id": referral_id})
    except DjangoIntegrityError as e:
      # 중복 매칭 생성 시도 시 처리
      if "unique_sender_receiver" in str(e):
        raise ValidationError(
          message="이미 해당 사용자에게 호감을 보낸 적이 있습니다.",
          details={"constraint": "unique_sender_receiver"},
        )
      else:
        raise ValidationError(
          message="데이터 무결성 오류가 발생했습니다.",
          details={"error": str(e)},
        )
    except Exception as e:
      logger.error(
        "Failed to create matching from referral",
        exception=e,
        referral_id=referral_id,
        user_id=user.id,
      )
      raise

  @staticmethod
  def check_ticket_availability(user, ticket_amount=None):
    """사용자의 티켓 보유량 확인"""
    if ticket_amount is None:
      ticket_amount = settings.MATCHING_TICKET_COST

    return user.ticket_amount >= ticket_amount

  @staticmethod
  def get_required_ticket_amount():
    """매칭 생성에 필요한 티켓 수량 반환"""
    return settings.MATCHING_TICKET_COST
