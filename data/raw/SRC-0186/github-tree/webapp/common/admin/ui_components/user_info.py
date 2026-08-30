from django.utils.html import format_html


class AdminUserInfo:
    """사용자 정보 표시 컴포넌트"""

    @staticmethod
    def create(user, show_email=True, show_status=True):
        """사용자 정보 표시 (XSS 방지)"""
        if not user:
            return "-"

        username_html = format_html("<strong>{}</strong>", user.username)

        email_html = ""
        if show_email:
            email_html = format_html("<br/><small>이메일: {}</small>", user.email)

        status_html = ""
        if show_status:
            status_color = "green" if user.is_confirmed else "orange"
            status_text = "승인됨" if user.is_confirmed else "미승인"
            status_html = format_html(
                '<br/><small style="color: {};">상태: {}</small>',
                status_color,
                status_text,
            )

        profile_html = ""
        profile = getattr(user, "profile", None)

        if profile:
            profile_info = []
            if profile.gender:
                profile_info.append(profile.gender)
            if profile.region:
                profile_info.append(profile.region)
            if profile.city:
                profile_info.append(profile.city)

            if profile_info:
                profile_html = format_html(
                    "<br/><small>{} | {} | {}</small>",
                    profile.gender or "-",
                    profile.region or "-",
                    profile.city or "-",
                )

        return format_html("<div>{}{}{}{}</div>", username_html, email_html, status_html, profile_html)
