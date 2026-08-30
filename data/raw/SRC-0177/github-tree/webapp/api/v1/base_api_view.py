from rest_framework.views import APIView


class BaseAPIView(APIView):

    @property
    def current_user(self):
        return self.request.user
