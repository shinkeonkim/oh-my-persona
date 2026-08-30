from django.urls import path, re_path

from .views import KakaoLogin, UserDeleteView, kakao_callback, kakao_login
from .views.user_detail_view import UserDetailView

app_name = "account"


urlpatterns = [
    path("accounts/user/delete/", UserDeleteView.as_view(), name="user_delete"),
    re_path(r"^accounts/user/?$", UserDetailView.as_view(), name="rest_user_details"),
    path("accounts/kakao/login/", kakao_login, name="kakao_login"),
    path("accounts/kakao/login/callback/", kakao_callback, name="kakao_callback"),
    path(
        "accounts/kakao/login/finish/",
        KakaoLogin.as_view(),
        name="kakao_login_todjango",
    ),
]
