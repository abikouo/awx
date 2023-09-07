# Copyright (c) 2017 Ansible, Inc.
# All Rights Reserved.

from django.urls import re_path

from awx.api.views import (
    ResourceStateList,
    ResourceStateDetail,
)


urls = [
    re_path(r'^$', ResourceStateList.as_view(), name='resource_state_list'),
    re_path(r'^(?P<pk>[0-9]+)/$', ResourceStateDetail.as_view(), name='resource_state_detail'),
]

__all__ = ['urls']
