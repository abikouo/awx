# Copyright (c) 2017 Ansible, Inc.
# All Rights Reserved.

from django.urls import re_path

from awx.api.views import (
    StateList,
    StateDetail,
)


urls = [
    re_path(r'^$', StateList.as_view(), name='state_list'),
    re_path(r'^(?P<pk>[0-9]+)/$', StateDetail.as_view(), name='state_detail'),
]

__all__ = ['urls']
