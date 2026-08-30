from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet, TicketProductViewSet

app_name = "payments"

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"ticket-products", TicketProductViewSet, basename="ticket-product")

urlpatterns = [
    path("", include(router.urls)),
]
