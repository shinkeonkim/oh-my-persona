from django.utils.html import format_html


class AdminTicketInfo:
    """어드민용 티켓 정보 표시 컴포넌트"""

    @staticmethod
    def create(ticket_amount, used_ticket_amount, show_icons=True):
        """티켓 정보 표시"""
        if show_icons:
            return format_html(
                '<div style="font-size: 12px; line-height: 1.4;">'
                '<div style="color: #2563eb; font-weight: 500;">'
                "🎫 보유: <strong>{}</strong>"
                "</div>"
                '<div style="color: #6b7280; margin-top: 2px;">'
                "📤 사용: <strong>{}</strong>"
                "</div>"
                "</div>",
                ticket_amount,
                used_ticket_amount,
            )
        else:
            return format_html(
                '<div style="font-size: 12px; line-height: 1.4;">'
                '<div style="color: #2563eb; font-weight: 500;">보유: <strong>{}</strong></div>'
                '<div style="color: #6b7280; margin-top: 2px;">사용: <strong>{}</strong></div>'
                "</div>",
                ticket_amount,
                used_ticket_amount,
            )

    @staticmethod
    def summary(ticket_amount, used_ticket_amount):
        """티켓 요약 정보"""
        total = ticket_amount + used_ticket_amount
        return format_html(
            '<div style="font-size: 11px; color: #6b7280;">' "총 <strong>{}</strong>개 (보유: {}, 사용: {})" "</div>",
            total,
            ticket_amount,
            used_ticket_amount,
        )
