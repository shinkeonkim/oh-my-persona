from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.kakao import views as kakao_view
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomKakaoOAuth2Adapter(kakao_view.KakaoOAuth2Adapter):
    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        resp = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        resp.raise_for_status()
        extra_data = resp.json()
        social_login = self.get_provider().sociallogin_from_response(
            request, extra_data
        )
        user = social_login.user
        user.username = extra_data.get("properties", {}).get("nickname", user.email)

        return social_login
