from functools import wraps
from typing import Callable, Optional

from action_trackings.services import ProfileViewTrackingService


def track_profile_view(get_profile: Callable, get_metadata: Optional[Callable] = None):
  """
    프로필 조회 트래킹을 위한 전용 데코레이터

    Usage:
        @track_profile_view(
            get_profile=lambda view, *args, **kwargs: Profile.objects.get(id=kwargs['profile_id']),
            get_metadata=lambda view, *args, **kwargs: {'source': 'detail_page'}
        )
        def get(self, request, profile_id):
            ...

    Args:
        get_profile: 조회된 프로필 객체를 가져오는 함수
                    인자: (view_instance, *args, **kwargs)
        get_metadata: 추가 메타데이터를 가져오는 함수 (optional)
                     인자: (view_instance, *args, **kwargs)
    """

  def decorator(view_func):

    @wraps(view_func)
    def wrapped_view(view_instance, request, *args, **kwargs):
      # 원본 뷰 함수 실행
      response = view_func(view_instance, request, *args, **kwargs)

      # 트래킹 수행
      try:
        user = getattr(request, "user", None)

        # 인증된 사용자만 트래킹
        if user and user.is_authenticated:
          # 프로필 가져오기
          profile = get_profile(view_instance, *args, **kwargs)

          # metadata 가져오기
          metadata = {}
          if get_metadata:
            try:
              metadata = get_metadata(view_instance, *args, **kwargs)
            except Exception:
              pass  # metadata 가져오기 실패 시 무시

          # 트래킹 수행
          ProfileViewTrackingService.track_profile_view(
            viewer=user,
            viewed_profile=profile,
            request=request,
            **metadata,
          )

      except Exception:
        # 트래킹 실패해도 원본 응답은 반환
        pass

      return response

    return wrapped_view

  return decorator
