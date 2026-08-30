from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
  AddressListView,
  BirthTimeListView,
  CompatibilityScoreAPIView,
  JobCategoryListView,
  JobListView,
  MyProfileImageViewSet,
  MyProfileView,
  ProfileImageViewSet,
  ProfileProofImageView,
  ProfileView,
  ReferralCompatibilityTagsAPIView,
  ReferralOverallOpinionAPIView,
  ReferralSynergyAPIView,
)

# Create router for ViewSet
router = DefaultRouter()
router.register(r"me/images", MyProfileImageViewSet, basename="my-profile-image")
router.register(r"(?P<profile_id>\d+)/images", ProfileImageViewSet, basename="profile-image")

urlpatterns = [
  # 내 프로필 관련 API
  path("me/", MyProfileView.as_view(), name="my-profile"),
  path("me/proof-image/", ProfileProofImageView.as_view(), name="profile-proof-image"),
  # 다른 사용자 프로필 조회 API
  path("<int:profile_id>/", ProfileView.as_view(), name="profile-detail"),
  # 추천 관련 API (profile 기반)
  path("<int:profile_id>/referral-synergies/", ReferralSynergyAPIView.as_view(), name="profile-referral-synergies"),
  path("<int:profile_id>/referral-overall-opinion/",
       ReferralOverallOpinionAPIView.as_view(),
       name="profile-referral-overall-opinion"),
  path("<int:profile_id>/compatibility-score/", CompatibilityScoreAPIView.as_view(),
       name="profile-compatibility-score"),
  path("<int:profile_id>/compatibility-tags/",
       ReferralCompatibilityTagsAPIView.as_view(),
       name="profile-compatibility-tags"),
  # 기타 API
  path("", include(router.urls)),
  path("addresses/", AddressListView.as_view(), name="address-list"),
  path("birth-times/", BirthTimeListView.as_view(), name="birth-time-list"),
  path("job-categories/", JobCategoryListView.as_view(), name="job-category-list"),
  path(
    "job-categories/<int:job_category_id>/jobs/",
    JobListView.as_view(),
    name="job-list",
  ),
]
