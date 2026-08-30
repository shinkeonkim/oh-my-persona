from django import forms

from unfold.widgets import UnfoldAdminTextInputWidget


class SendReportEmailForm(forms.Form):
    """레포트 이메일 전송 폼"""

    email = forms.EmailField(
        label="수신자 이메일",
        required=True,
        widget=UnfoldAdminTextInputWidget(
            attrs={
                "placeholder": "example@email.com",
            }
        ),
        help_text="레포트 PDF를 전송할 이메일 주소를 입력하세요.",
    )

    class Meta:
        required_css_class = "required"
