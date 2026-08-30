from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from profiles.models import Profile


class BaseAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @property
    def current_user(self):
        return self.request.user

    @property
    def current_user_profile(self):
        if not hasattr(self, "_current_user_profile"):
            profile, created = Profile.objects.get_or_create(user=self.current_user)
            self._current_user_profile = profile
        return self._current_user_profile
