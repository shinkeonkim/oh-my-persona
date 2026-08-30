from datetime import timedelta

from django.db import models, transaction
from django.utils import timezone

from celery import shared_task

from matchmakings.models.pre_matching import PreMatching, PreMatchingStatus
from matchmakings.models.pre_matching_score import PreMatchingScore
from matchmakings.services.pre_matching.algorithms import AlgorithmFactory
from profiles.choices.profile_status_choices import ProfileStatusChoices
from saju.services import UserSajuChartService
from users.models.user import FemaleUser, MaleUser, User


def reset_prematching_status(prematching_id):
    """PreMatching 상태를 PENDING으로 리셋"""
    PreMatching.objects.filter(id=prematching_id).update(status=PreMatchingStatus.PENDING)


@shared_task
def schedule_pre_matching_task(user_id):
    """
    사용자의 프로필이 승인 전에 업데이트 완료되면 실행되는 pre_matching task
    """
    try:
        user = User.objects.get(id=user_id)

        # 프로필에 성별 정보가 있는지 확인
        if not hasattr(user, "profile") or not user.profile.gender:
            return f"User {user_id} has no gender information, skipping pre_matching"

        UserSajuChartService(profile=user.profile).update_or_create_saju_profile()

        # 최근 10분 내에 해당 프로필에 대한 task가 실행되었는지 확인
        ten_minutes_ago = timezone.now() - timedelta(minutes=10)
        recent_prematchings = PreMatching.objects.filter(
            models.Q(male_user=user) | models.Q(female_user=user),
            last_calculated_at__gte=ten_minutes_ago,
        )

        if recent_prematchings.exists():
            return f"Recent pre_matching task found for user {user_id}, skipping"

        # 성별에 따라 매칭 대상 결정
        if user.profile.gender == "M":
            # 남자 유저 - 여자 유저들과 매칭
            target_users = FemaleUser.objects.filter(
                profile__isnull=False,
                profile__gender="F",
                profile__status__in=[
                    ProfileStatusChoices.ACTIVE,
                    ProfileStatusChoices.PENDING,
                ],
            ).exclude(id=user.id)
        else:
            # 여자 유저 - 남자 유저들과 매칭
            target_users = MaleUser.objects.filter(
                profile__isnull=False,
                profile__gender="M",
                profile__status__in=[
                    ProfileStatusChoices.ACTIVE,
                    ProfileStatusChoices.PENDING,
                ],
            ).exclude(id=user.id)

        # 각 대상 유저와의 PreMatching 생성 및 점수 계산
        for target_user in target_users:
            # PreMatching이 이미 존재하는지 확인
            prematching, _created = PreMatching.objects.get_or_create(
                male_user=user if user.profile.gender == "M" else target_user,
                female_user=target_user if user.profile.gender == "M" else user,
                defaults={"status": PreMatchingStatus.PENDING},
            )

            calculate_all_pre_matching_scores.delay(prematching.id)

        return f"PreMatchings calculated for user {user_id}"

    except User.DoesNotExist:
        return f"User {user_id} not found"
    except Exception as e:
        return f"Error processing user {user_id}: {str(e)}"


@shared_task
def calculate_all_pre_matching_scores(prematching_id):
    """
    PreMatching에 대해 모든 등록된 알고리즘으로 점수를 계산합니다.
    """
    try:
        with transaction.atomic():
            # PreMatching 상태를 CALCULATING으로 변경
            prematching = PreMatching.objects.select_for_update().get(id=prematching_id)
            prematching.status = PreMatchingStatus.CALCULATING
            prematching.save()

            # 모든 등록된 알고리즘에 대해 점수 계산
            available_algorithms = AlgorithmFactory.get_available_algorithms()
            calculated_scores = []

            for algorithm_name in available_algorithms:
                try:
                    # 알고리즘 팩토리를 통해 알고리즘 인스턴스 생성
                    algorithm = AlgorithmFactory.create_algorithm(algorithm_name, prematching)

                    # 점수 계산
                    score = algorithm.run()

                    # PreMatchingScore 생성 또는 업데이트
                    score_obj, created = PreMatchingScore.objects.get_or_create(
                        prematching=prematching,
                        algorithm_category=algorithm_name,
                        defaults={"score": score},
                    )

                    if not created:
                        # 이미 존재하는 경우 점수 업데이트
                        score_obj.score = score
                        score_obj.save()

                    calculated_scores.append(f"{algorithm_name}: {score}")

                except Exception as e:
                    # 개별 알고리즘에서 에러가 발생해도 다른 알고리즘은 계속 실행
                    calculated_scores.append(f"{algorithm_name}: ERROR - {str(e)}")
                    continue

            # PreMatching 상태를 COMPLETED로 변경하고 마지막 계산 시간 업데이트
            prematching.status = PreMatchingStatus.COMPLETED
            prematching.last_calculated_at = timezone.now()
            prematching.save()

            return f"Calculated scores for prematching {prematching_id}: {', '.join(calculated_scores)}"

    except PreMatching.DoesNotExist:
        return f"PreMatching {prematching_id} not found"
    except Exception as e:
        # 에러 발생 시 상태를 PENDING으로 되돌림
        reset_prematching_status(prematching_id)
        return f"Error calculating scores for prematching {prematching_id}: {str(e)}"


@shared_task
def calculate_pre_matching_score(prematching_id, algorithm_name):
    """
    PreMatching에 대해 특정 알고리즘으로 점수를 계산합니다.
    (개별 알고리즘 테스트용)
    """
    try:
        with transaction.atomic():
            # PreMatching 상태를 CALCULATING으로 변경
            prematching = PreMatching.objects.select_for_update().get(id=prematching_id)
            prematching.status = PreMatchingStatus.CALCULATING
            prematching.save()

            # 알고리즘 팩토리를 통해 알고리즘 인스턴스 생성
            algorithm = AlgorithmFactory.create_algorithm(algorithm_name, prematching)

            # 점수 계산
            score = algorithm.run()

            # PreMatchingScore 생성 또는 업데이트
            score_obj, created = PreMatchingScore.objects.get_or_create(
                prematching=prematching,
                algorithm_category=algorithm_name,
                defaults={"score": score},
            )

            if not created:
                # 이미 존재하는 경우 점수 업데이트
                score_obj.score = score
                score_obj.save()

            # PreMatching 상태를 COMPLETED로 변경하고 마지막 계산 시간 업데이트
            prematching.status = PreMatchingStatus.COMPLETED
            prematching.last_calculated_at = timezone.now()
            prematching.save()

            return f"Calculated score {score} for prematching {prematching_id} using {algorithm_name}"

    except PreMatching.DoesNotExist:
        return f"PreMatching {prematching_id} not found"
    except Exception as e:
        # 에러 발생 시 상태를 PENDING으로 되돌림
        reset_prematching_status(prematching_id)
        return f"Error calculating score for prematching {prematching_id}: {str(e)}"
