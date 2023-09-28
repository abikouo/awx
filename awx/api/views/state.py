# Copyright (c) 2023 Ansible, Inc.
# All Rights Reserved.

# Django
from django.utils.translation import gettext_lazy as _


# Django REST Framework
from rest_framework.response import Response
from rest_framework import status


# AWX
from awx.api.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from awx.main import models

from awx.api import serializers


class StateList(ListCreateAPIView):
    model = models.State
    serializer_class = serializers.StateSerializer


class StateView(RetrieveUpdateDestroyAPIView):
    name = _("State")
    model = models.State
    serializer_class = serializers.StateSerializer

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        state = obj.display_state()
        if not state:
            # terraform http client is expecting '404' response instead of
            # an empty dict
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(state)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.state = request.data
        obj.save(update_fields=['state'])
        return Response({"pk": obj.pk}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        return super(StateView, self).delete(request, *args, **kwargs)
