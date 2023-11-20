# Copyright (c) 2023 Ansible, Inc.
# All Rights Reserved.

# Django
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

# Django REST Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework import views

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
    http_method_names = views.APIView.http_method_names + ["lock", "unlock"]

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        state = obj.display_state()
        if not state:
            # terraform http client is expecting '404' response instead of
            # an empty dict
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(state)

    def post(self, request, *args, **kwargs):
        qry_lock_id = request.query_params.get("ID")
        if qry_lock_id:
            obj = get_object_or_404(models.State, pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, obj)
        else:
            obj = self.get_object()

        if obj.is_locked() and qry_lock_id != obj.lockID:
            return Response(status=status.HTTP_423_LOCKED)

        if not obj.update(state=request.data, update_fields=['state'], nowait=False):
            return Response(status=status.HTTP_409_CONFLICT)
        return Response({"pk": obj.pk}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        return super(StateView, self).delete(request, *args, **kwargs)

    def lock(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.is_locked():
            # Object already locked
            return Response(obj.lock_info, status=status.HTTP_423_LOCKED)

        if not obj.update(lock_info=request.data, update_fields=['lock_info']):
            return Response(status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_200_OK)

    def unlock(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.is_locked():
            # nothing to do when the object is not locked
            return Response(status=status.HTTP_200_OK)
        # ensure the 'ID' is matching with the current lock id
        # when user performs 'terraform force-unlock <lockID>', terraform issues an http
        # request with body={} and query_params={}
        if not request.data or (obj.lockID == request.data.get("ID")):
            if not obj.update(lock_info={}, update_fields=['lock_info'], nowait=False):
                return Response(status=status.HTTP_409_CONFLICT)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
