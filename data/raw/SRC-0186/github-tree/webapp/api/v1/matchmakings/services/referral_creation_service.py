import random
from typing import Tuple

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone

from referral_conversations.services import ConversationCreationService

from common.exceptions.custom_exceptions import ValidationError
from common.utils.logger import get_logger
from matchmakings.models import (
  Matching,
  PreMatching,
  PreparedCompatibilityTag,
  Referral,
  ReferralCompatibilityTag,
  ReferralConversation,
)

User = get_user_model()

logger = get_logger(__name__)

# 추천 정리 관련 상수
MAX_RECENT_REFERRALS_PER_ALGORITHM = 10  # 알고리즘별로 보존할 최근 추천 수
# TODO: 해당 상수도 논의후에 재정의 필요

# 궁합 태그 관련 상수
COMPATIBILITY_TAGS_COUNT = 6  # Referral당 선택할 궁합 태그 개수


class ReferralCreationService:
  """추천 생성 관련 서비스"""

  @staticmethod
  @transaction.atomic
  def create_referral(user, algorithm_type) -> Referral | None:
    """새로운 추천 생성"""
    try:
      if not user.can_receive_referral():
        raise ValidationError(
          message="추천 횟수가 부족합니다.",
          details={"remaining_quota": user.remaining_referral_quota_count},
        )

      # 추천할 사용자 찾기
      score, recommended_user = ReferralCreationService.find_recommended_user(user, algorithm_type)

      if not recommended_user:
        # 추천할 사용자가 없는 경우, 최근 추천을 제외하고 나머지 모든 추천을 삭제
        logger.info(
          "No users available for referral, cleaning up referrals except recent ones",
          user_id=user.id,
          algorithm_type=algorithm_type,
        )

        ReferralCreationService.cleanup_referrals_except_latest(user, algorithm_type)

        # 정리 후 다시 추천할 사용자 찾기
        score, recommended_user = ReferralCreationService.find_recommended_user(user, algorithm_type)

        if not recommended_user:
          # 정리 후에도 추천할 사용자가 없으면 None 반환
          return None

      referral = Referral.objects.create(
        user=user,
        referral_user=recommended_user,
        referred_at=timezone.now(),
        referred_algorithm=algorithm_type,
        compatibility_score=score,
      )

      ReferralCreationService._create_compatibility_tags(referral, user, recommended_user)

      conversation_service = ConversationCreationService(referral)
      conversation_messages = conversation_service.create_conversation()
      opposite_conversation_messages = conversation_service.create_opposite_conversation()

      messages_json = [{"role": msg.role, "content": msg.content} for msg in conversation_messages]
      opposite_messages_json = [{"role": msg.role, "content": msg.content} for msg in opposite_conversation_messages]

      ReferralConversation.objects.create(
        referral=referral,
        conversation_messages=messages_json,
        opposite_conversation_messages=opposite_messages_json,
      )

      # 추천 횟수 차감
      user.consume_referral_quota()

      referral.refresh_from_db()

      return referral

    except Exception as e:
      logger.error(
        "Failed to create referral",
        exception=e,
        user_id=user.id,
        algorithm_type=algorithm_type,
      )
      raise

  @staticmethod
  def _create_compatibility_tags(referral, user, recommended_user):
    """일주 정보를 이용하여 궁합 태그 생성"""
    # TODO: 이 로직 정리 필요
    try:
      # 사용자들의 사주 프로필 확인
      user_saju = user.saju_profile
      recommended_user_saju = recommended_user.saju_profile
    except Exception as e:
      logger.error(
        "Failed to retrieve saju profiles for users",
        exception=e,
        user_id=user.id,
        recommended_user_id=recommended_user.id,
      )
      return

    try:
      user_gender = user.profile.gender
    except Exception as e:
      logger.error(
        "Failed to retrieve user gender",
        exception=e,
        user_id=user.id,
      )
      return

    try:
      if user_gender == "M":
        male_user_saju = user_saju
        female_user_saju = recommended_user_saju
      else:
        male_user_saju = recommended_user_saju
        female_user_saju = user_saju

      # PreparedCompatibilityTag 조회
      prepared_tag = PreparedCompatibilityTag.objects.filter(
        male_d_stem=male_user_saju.d_stem,
        male_d_branch=male_user_saju.d_branch,
        female_d_stem=female_user_saju.d_stem,
        female_d_branch=female_user_saju.d_branch,
      ).prefetch_related("compatibility_tags").first()

      if not prepared_tag:
        logger.warning(
          "PreparedCompatibilityTag not found",
          male_d_stem=male_user_saju.d_stem,
          male_d_branch=male_user_saju.d_branch,
          female_d_stem=female_user_saju.d_stem,
          female_d_branch=female_user_saju.d_branch,
        )
        return

      # 모든 궁합 태그 가져오기
      all_tags = list(prepared_tag.compatibility_tags.all())

      if not all_tags:
        logger.warning(
          "No compatibility tags found for prepared tag",
          prepared_tag_id=prepared_tag.id,
        )
        return

      # 랜덤으로 최대 COMPATIBILITY_TAGS_COUNT개 선택
      selected_count = min(COMPATIBILITY_TAGS_COUNT, len(all_tags))
      selected_tags = random.sample(all_tags, selected_count)

      # ReferralCompatibilityTag 생성
      referral_compatibility_tags = [
        ReferralCompatibilityTag(
          referral=referral,
          compatibility_tag=tag,
        ) for tag in selected_tags
      ]
      ReferralCompatibilityTag.objects.bulk_create(referral_compatibility_tags)

      logger.info(
        "Created compatibility tags for referral",
        referral_id=referral.id,
        selected_count=selected_count,
        total_available=len(all_tags),
      )

    except Exception as e:
      logger.error(
        "Failed to create compatibility tags",
        exception=e,
        referral_id=referral.id,
      )
      # 궁합 태그 생성 실패는 추천 생성을 중단하면 안됨.
      pass

  @staticmethod
  def _apply_male_algorithm(users, user, algorithm_type) -> Tuple[int, User]:
    """알고리즘에 따라 사용자 선택 (현재 유저가 남자인 경우)"""

    prematchings = PreMatching.objects.filter(male_user=user, female_user__in=users)

    prematchings = prematchings.annotate(max_score=models.Max(
      models.Case(
        models.When(
          pre_matching_scores__algorithm_category=algorithm_type,
          then="pre_matching_scores__score",
        ),
        default=0,
        output_field=models.IntegerField(),
      ))).order_by("-max_score")

    if prematchings.exists():
      prematching = prematchings.first()
      score = prematching.pre_matching_scores.get(algorithm_category=algorithm_type).score
      return (score, prematching.female_user)

    return (0, None)

  @staticmethod
  def _apply_female_algorithm(users, user, algorithm_type) -> Tuple[int, User]:
    """알고리즘에 따라 사용자 선택 (현재 유저가 여자인 경우)"""

    prematchings = PreMatching.objects.filter(female_user=user, male_user__in=users)

    prematchings = prematchings.annotate(max_score=models.Max(
      models.Case(
        models.When(
          pre_matching_scores__algorithm_category=algorithm_type,
          then="pre_matching_scores__score",
        ),
        default=0,
        output_field=models.IntegerField(),
      ))).order_by("-max_score")

    if prematchings.exists():
      prematching = prematchings.first()
      score = prematching.pre_matching_scores.get(algorithm_category=algorithm_type).score
      return (score, prematching.male_user)

    return (0, None)

  @staticmethod
  def get_excluded_users(current_user: User):
    """매칭에서 제외할 사용자들 반환 (현재 수신되지 않았거나 거절된 매칭의 상대방)"""
    try:
      excluded_senders = Matching.objects.filter(receiver=current_user,
                                                 received_at__isnull=True).values_list("sender_id", flat=True)

      excluded_receivers = Matching.objects.filter(sender=current_user,
                                                   rejected_at__isnull=False).values_list("receiver_id", flat=True)

      return list(excluded_senders) + list(excluded_receivers)
    except Exception as e:
      logger.error("Failed to get excluded users", exception=e, user_id=current_user.id)
      return []

  @staticmethod
  def get_matched_users(current_user: User):
    """매칭이 이루어진 사용자들 반환"""
    try:
      matched_senders = Matching.objects.filter(receiver=current_user,
                                                received_at__isnull=False).values_list("sender_id", flat=True)

      matched_receivers = Matching.objects.filter(sender=current_user,
                                                  received_at__isnull=False).values_list("receiver_id", flat=True)

      return list(matched_senders) + list(matched_receivers)
    except Exception as e:
      logger.error("Failed to get matched users", exception=e, user_id=current_user.id)
      return []

  @staticmethod
  def find_recommended_user(current_user: User, algorithm_type: str) -> Tuple[int, User]:
    """알고리즘에 따라 추천할 사용자 찾기 (뷰에서 사용)"""
    try:
      # 현재 사용자의 성별 확인
      current_user_gender = current_user.profile.gender if hasattr(current_user, "profile") else None
      if not current_user_gender:
        return (0, None)

      # 반대 성별 사용자들 조회
      opposite_gender = "F" if current_user_gender == "M" else "M"

      # 이미 추천받은 사용자들 제외
      already_referred_users = Referral.objects.filter(user=current_user).values_list("referral_user_id", flat=True)

      # 매칭이 이루어지지 않은 사용자들 제외 (현재 수신되지 않았거나 거절된 경우)
      excluded_users = ReferralCreationService.get_excluded_users(current_user)

      # 추천 가능한 사용자들 조회
      available_users = (User.objects.filter(profile__gender=opposite_gender).exclude(
        id__in=already_referred_users).exclude(id__in=excluded_users).exclude(id=current_user.id))

      if not available_users.exists():
        return (0, None)

      # 알고리즘에 따른 정렬 및 선택
      if current_user_gender == "M":
        score, recommended_user = ReferralCreationService._apply_male_algorithm(
          available_users,
          current_user,
          algorithm_type,
        )
      else:
        score, recommended_user = ReferralCreationService._apply_female_algorithm(
          available_users,
          current_user,
          algorithm_type,
        )

      return score, recommended_user

    except Exception as e:
      logger.error("Failed to find recommended user", exception=e, user_id=current_user.id)
      return (0, None)

  @staticmethod
  def get_recently_unmatched_referred_user_ids_by_algorithm(current_user: User, algorithm_type: str):
    """특정 알고리즘으로 최근에 추천된 사용자 ID들 반환 (최대 10개, 매칭되지 않은 것만)"""
    try:
      # 해당 알고리즘으로 최근에 추천된 사용자들 조회 (최신순으로 정렬)
      # 그 중 호감을 보내지 않은 것 10개의 user_id만 반환
      recently_unmatched_referred_user_ids = (Referral.objects.filter(
        user=current_user,
        referred_algorithm=algorithm_type,
      ).exclude(referral_user__in=Matching.objects.filter(
        sender=current_user).values_list("receiver_id", flat=True)).exclude(referral_user__in=Matching.objects.filter(
          receiver=current_user).values_list("sender_id", flat=True)).order_by("-created_at")
                                              [:MAX_RECENT_REFERRALS_PER_ALGORITHM].values_list("referral_user_id",
                                                                                                flat=True))

      return list(recently_unmatched_referred_user_ids)
    except Exception as e:
      logger.error(
        "Failed to get recently referred user ids by algorithm",
        exception=e,
        user_id=current_user.id,
        algorithm_type=algorithm_type,
      )
      return []

  @staticmethod
  def cleanup_referrals_except_latest(current_user: User, algorithm_type: str):
    """최신 추천을 제외하고 나머지 모든 추천을 삭제합니다"""
    try:
      # 해당 알고리즘으로 최근에 추천된 사용자 ID들 조회
      recently_referred_user_ids = ReferralCreationService.get_recently_unmatched_referred_user_ids_by_algorithm(
        current_user, algorithm_type)

      using_matchings = Matching.objects.filter(models.Q(sender=current_user) | models.Q(receiver=current_user))
      referral_ids_in_matching = using_matchings.values_list('referral_id', flat=True).distinct()

      # 최근 추천된 사용자 및 매칭에 사용된 추천을 제외한 해당 알고리즘의 추천 삭제
      referrals_to_delete = Referral.objects.filter(user=current_user, referred_algorithm=algorithm_type).exclude(
        referral_user_id__in=recently_referred_user_ids).exclude(id__in=referral_ids_in_matching)

      deleted_count = referrals_to_delete.count()
      referrals_to_delete.delete()

      if deleted_count > 0:
        logger.info(
          "Cleaned up referrals except recent ones",
          user_id=current_user.id,
          algorithm_type=algorithm_type,
          deleted_count=deleted_count,
          kept_recent_users=len(recently_referred_user_ids),
          max_recent_count=MAX_RECENT_REFERRALS_PER_ALGORITHM,
        )

      return deleted_count
    except Exception as e:
      logger.error(
        "Failed to cleanup referrals except latest",
        exception=e,
        user_id=current_user.id,
        algorithm_type=algorithm_type,
      )
      return 0
