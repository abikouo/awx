#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2023, Aubin Bikouo <@abikouo>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = '''
---
module: state
author: "Aubin Bikouo (@abikouo)"
short_description: create, update, or destroy Automation Platform Controller state.
description:
    - Create, update, or destroy Automation Platform Controller state. See
      U(https://www.ansible.com/tower) for an overview.
options:
    state_id:
      description:
        - ID of the resource state
      type: int
    state_info:
      description:
        - The information to store into the state resource.
      type: dict
    lock_info:
      description:
        - The locking info to use for the state resource.
      type: dict
    state:
      description:
        - Desired state of the resource.
      choices:
        - present
        - absent
        - exists
      default: "present"
      type: str
extends_documentation_fragment: awx.awx.auth
'''


EXAMPLES = '''
- name: Add empty state resource
  host:
    state: present

- name: Update existing state resource (remove lock info)
  host:
    state_id: 7
    lock_info: {}
    state: present

- name: Delete state resource
  host:
    state_id: 7
    state: absent
'''


from ..module_utils.controller_api import ControllerAPIModule


def main():
    # Any additional arguments that are not fields of the item can be added here
    argument_spec = dict(
        state_id=dict(type="int"),
        state_info=dict(type='dict'),
        lock_info=dict(type='dict'),
        state=dict(choices=['present', 'absent', 'exists'], default='present'),
    )

    # Create a module for ourselves
    required_if = [("state", "absent", ["state_id"]), ("state", "exists", ["state_id"])]
    module = ControllerAPIModule(argument_spec=argument_spec, required_if=required_if)

    # Extract our parameters
    state_id = module.params.get('state_id')
    state_info = module.params.get('state_info')
    lock_info = module.params.get('lock_info')
    state = module.params.get('state')

    existing = None
    if state_id is not None:
        existing = module.get_one(
            'state',
            check_exists=(state == 'exists'),
            **{
                'data': {
                    'id': state_id,
                }
            },
        )

    if state == 'absent':
        # If the state was absent we can let the module delete it if needed, the module will handle exiting from this
        module.delete_if_needed(existing)

    if state_id is not None and not existing:
        module.fail_json(msg=f"No state resource with Id '{state_id}'")

    state_fields = {}
    if state_info is not None:
        state_fields["state"] = state_info
    if lock_info is not None:
        state_fields["lock_info"] = lock_info

    # If the state was present and we can let the module build or update the existing resource, this will return on its own
    module.create_or_update_if_needed(existing, state_fields, endpoint='state', item_type='state')


if __name__ == '__main__':
    main()
