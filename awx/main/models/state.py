# Copyright (c) 2023 Ansible, Inc.
# All Rights Reserved.

# Django
from django.db import transaction, DatabaseError

# AWX
from awx.api.versioning import reverse
from awx.main.fields import JSONBlob
from awx.main.models.base import CreatedModifiedModel
from awx.main.utils import parse_yaml_or_json

__all__ = ('State',)


class State(CreatedModifiedModel):
    class Meta:
        app_label = 'main'
        ordering = ("pk",)

    state = JSONBlob(
        default=dict,
        blank=True,
        editable=True,
    )

    lock_info = JSONBlob(
        default=dict,
        blank=True,
        editable=True,
    )

    def get_absolute_url(self, request=None):
        return reverse('api:state_detail', kwargs={'pk': self.pk}, request=request)

    def display_state(self):
        return parse_yaml_or_json(self.state, silent_failure=False)

    def update(self, update_fields, state={}, lock_info={}, nowait=True):
        lock_info = lock_info or {}
        try:
            objects = self.__class__.objects.select_for_update(nowait=nowait).filter(pk=self.pk)
            with transaction.atomic():
                for obj in objects:
                    obj.lock_info = lock_info
                    obj.state = state
                    obj.save(update_fields=update_fields)
                    obj.save()
        except DatabaseError as err:
            if "could not obtain lock" in str(err):
                # object already locked
                return False
            raise
        return True

    def is_locked(self):
        return bool(self.lock_info)

    @property
    def lockID(self):
        lock_id = None
        if self.lock_info:
            lock_id = self.lock_info.get("ID")
        return lock_id
