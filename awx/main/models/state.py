# Copyright (c) 2023 Ansible, Inc.
# All Rights Reserved.

# Django
from django.db import models

# AWX
from awx.api.versioning import reverse
from awx.main.fields import JSONBlob
from awx.main.models.base import CreatedModifiedModel
from awx.main.utils import parse_yaml_or_json

__all__ = ('State',)


class State(CreatedModifiedModel):
    class Meta:
        app_label = 'main'

    state = JSONBlob(
        default=dict,
        blank=True,
        editable=True,
    )

    def get_absolute_url(self, request=None):
        return reverse('api:state_detail', kwargs={'pk': self.pk}, request=request)

    def display_state(self):
        return parse_yaml_or_json(self.state, silent_failure=False)
