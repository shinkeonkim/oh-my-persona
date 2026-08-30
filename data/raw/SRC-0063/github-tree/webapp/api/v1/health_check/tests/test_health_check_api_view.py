from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from api.v1.health_check.views.health_check_api_view import HealthCheckAPIView


class HealthCheckAPIViewTests(APITestCase):
    def test_health_check_returns_ok_status(self):
        url = reverse("health-check")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_health_check_explicitly_allows_anonymous_access(self):
        self.assertEqual(HealthCheckAPIView.permission_classes, [])
