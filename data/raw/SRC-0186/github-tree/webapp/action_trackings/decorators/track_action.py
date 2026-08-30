from functools import wraps
from typing import Callable, Optional

from action_trackings.services import ActionTrackingService


def track_action(
  action_type: str,
  get_content_object: Optional[Callable] = None,
  get_metadata: Optional[Callable] = None,
):
  """
    액션 트래킹을 위한 범용 데코레이터

    Usage:
        @track_action(
            action_type=ActionTypeChoices.MATCHING_CREATE,
            get_content_object=lambda view, *args, **kwargs: Matching.objects.get(id=kwargs['matching_id']),
            get_metadata=lambda view, *args, **kwargs: {'extra_field': 'value'}
        )
        def post(self, request, matching_id):
            ...

    Args:
        action_type: 트래킹할 액션 타입
        get_content_object: content_object를 가져오는 함수 (optional)
                           인자: (view_instance, *args, **kwargs)
        get_metadata: 메타데이터를 가져오는 함수 (optional)
                     인자: (view_instance, *args, **kwargs)
    """

  def decorator(view_func):

    @wraps(view_func)
    def wrapped_view(view_instance, request, *args, **kwargs):
      # 원본 뷰 함수 실행
      response = view_func(view_instance, request, *args, **kwargs)

      # 트래킹 수행 (비동기로 처리하거나 에러가 발생해도 원본 응답에 영향을 주지 않음)
      try:
        user = getattr(request, "user", None)

        # 인증된 사용자만 트래킹
        if user and user.is_authenticated:
          content_object = None
          metadata = None

          # content_object 가져오기
          if get_content_object:
            try:
              content_object = get_content_object(view_instance, *args, **kwargs)
            except Exception:
              pass  # content_object 가져오기 실패 시 무시

          # metadata 가져오기
          if get_metadata:
            try:
              metadata = get_metadata(view_instance, *args, **kwargs)
            except Exception:
              pass  # metadata 가져오기 실패 시 무시

          # 트래킹 수행
          ActionTrackingService.track_action(
            user=user,
            action_type=action_type,
            content_object=content_object,
            metadata=metadata,
            request=request,
          )

      except Exception:
        # 트래킹 실패해도 원본 응답은 반환
        pass

      return response

    return wrapped_view

  return decorator
