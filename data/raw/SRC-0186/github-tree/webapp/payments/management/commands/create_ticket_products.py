"""
티켓 상품 초기 데이터 생성 명령어
Usage: python manage.py create_ticket_products
"""

from django.core.management.base import BaseCommand

from payments.models import TicketProduct


class Command(BaseCommand):
    help = "티켓 상품 초기 데이터를 생성합니다"

    def handle(self, *args, **options):
        # 기본 티켓 상품 데이터
        ticket_products = [
            {"quantity": 10, "price": 1100, "display_order": 1},
            {"quantity": 20, "price": 2200, "display_order": 2},
            {"quantity": 50, "price": 5500, "display_order": 3},
            {"quantity": 100, "price": 10000, "display_order": 4},
        ]

        created_count = 0
        updated_count = 0

        for product_data in ticket_products:
            product, created = TicketProduct.objects.update_or_create(
                quantity=product_data["quantity"],
                defaults={
                    "price": product_data["price"],
                    "display_order": product_data["display_order"],
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ 생성: 티켓 {product.quantity}개 - {product.price:,}원 "
                        f"(할인율: {product.discount_rate}%)"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"→ 업데이트: 티켓 {product.quantity}개 - {product.price:,}원 "
                        f"(할인율: {product.discount_rate}%)"
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"\n완료! 생성: {created_count}개, 업데이트: {updated_count}개"))
