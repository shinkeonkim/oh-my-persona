from rest_framework import viewsets

from common.views import BaseAPIView


class BaseViewSet(BaseAPIView, viewsets.ModelViewSet):
    pass


class BaseGenericViewSet(BaseAPIView, viewsets.GenericViewSet):
    pass
