from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated


class BaseAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @property
    def current_user(self):
        return self.request.user
