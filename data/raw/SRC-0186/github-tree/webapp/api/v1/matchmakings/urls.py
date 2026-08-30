from django.urls import path

from .views import (
  CompletedMatchingListAPIView,
  CreateMatchingAPIView,
  CreateReferralAPIView,
  LatestReferralAPIView,
  MatchingActionAPIView,
  MatchingDetailAPIView,
  PastConnectionListAPIView,
  ReceivedMatchingListAPIView,
  ReferralDetailAPIView,
  ResetReferralQuotaAPIView,
  SentMatchingListAPIView,
)

urlpatterns = [
  # 추천 관련 API
  path("referrals/", CreateReferralAPIView.as_view(), name="referral-list-create"),
  path("referrals/<int:referral_id>/", ReferralDetailAPIView.as_view(), name="referral-detail"),
  path("referrals/latest/", LatestReferralAPIView.as_view(), name="referral-latest"),
  path("referrals/reset-quota/", ResetReferralQuotaAPIView.as_view(), name="referral-reset"),
  # 매칭 관련 API
  path("matchings/", CreateMatchingAPIView.as_view(), name="matching-create"),
  path(
    "matchings/<int:matching_id>/",
    MatchingDetailAPIView.as_view(),
    name="matching-detail",
  ),
  path("matchings/sent/", SentMatchingListAPIView.as_view(), name="matching-sent-list"),
  path(
    "matchings/received/",
    ReceivedMatchingListAPIView.as_view(),
    name="matching-received-list",
  ),
  path("matchings/completed/", CompletedMatchingListAPIView.as_view(), name="matching-completed-list"),
  path("matchings/past/", PastConnectionListAPIView.as_view(), name="matching-past-list"),
  path(
    "matchings/<int:matching_id>/action/",
    MatchingActionAPIView.as_view(),
    name="matching-action",
  ),
]
