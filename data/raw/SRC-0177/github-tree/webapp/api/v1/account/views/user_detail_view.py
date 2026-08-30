from api.v1.account.serializers import UserDetailSerializer
from dj_rest_auth.views import UserDetailsView


class UserDetailView(UserDetailsView):
    serializer_class = UserDetailSerializer
