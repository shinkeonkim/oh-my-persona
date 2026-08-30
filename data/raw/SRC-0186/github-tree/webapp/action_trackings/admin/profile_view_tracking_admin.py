from django.contrib import admin
from django.contrib.auth import get_user_model

from action_trackings.models import ProfileViewTracking
from unfold.admin import ModelAdmin

User = get_user_model()


@admin.register(ProfileViewTracking)
class ProfileViewTrackingAdmin(ModelAdmin):
  """프로필 조회 트래킹 Admin"""

  list_display = [
    "id",
    "user",
    "get_viewed_user",
    "get_viewed_profile",
    "ip_address",
    "created_at",
  ]
  list_filter = [
    "created_at",
  ]
  search_fields = [
    "user__email",
    "user__username",
    "metadata__viewed_user_id",
    "ip_address",
  ]
  readonly_fields = [
    "id",
    "user",
    "action_type",
    "content_type",
    "object_id",
    "content_object",
    "metadata",
    "ip_address",
    "user_agent",
    "get_viewed_user",
    "get_viewed_profile",
    "created_at",
    "updated_at",
  ]
  date_hierarchy = "created_at"
  ordering = ["-created_at"]
  list_filter_submit = True
  list_filter_sheet = False

  def get_viewed_user(self, obj):
    """조회된 사용자 표시"""
    viewed_user_id = obj.metadata.get("viewed_user_id")
    if viewed_user_id:
      try:
        user = User.objects.get(id=viewed_user_id)
        return f"{user.username} ({user.email})"
      except User.DoesNotExist:
        return f"User ID: {viewed_user_id} (삭제됨)"
    return "-"

  get_viewed_user.short_description = "조회된 사용자"

  def get_viewed_profile(self, obj):
    """조회된 프로필 ID 표시"""
    viewed_profile_id = obj.metadata.get("viewed_profile_id")
    if viewed_profile_id:
      return f"Profile ID: {viewed_profile_id}"
    return "-"

  get_viewed_profile.short_description = "조회된 프로필"

  def has_add_permission(self, request):
    """추가 권한 비활성화 (트래킹은 자동으로만 생성)"""
    return False

  def has_change_permission(self, request, obj=None):
    """수정 권한 비활성화 (읽기 전용)"""
    return False

  def has_delete_permission(self, request, obj=None):
    """삭제 권한은 관리자만 가능"""
    return request.user.is_superuser
