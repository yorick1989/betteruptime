#!/usr/bin/python

# Copyright: (c) 2021, Yorick Gruijthuijzen <yorick@gruijthuijzen.nl>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: monitors

short_description: "This module creates / updates or removes a monitor on / from Better Uptime."

version_added: "1.0.0"

description: "This module creates / updates or removes a monitor on / from Better Uptime."

options:
  api_token:
    description: "API Bearer token."
    required: True
    type: str
    no_log: True
    env:
      - name: BU_API_TOKEN
  id:
    description: "The ID of the monitor you want to update."
    required: True
    type: int
    env:
      - name: BU_ID
  check_for:
    description:
      - "Provide a str or list of options to compare existing items with."
      - "Overwrite / update when all the options do match and if it doesn't; a new item will be created."
      - "default: url"
    required: False
    type: list
    default: url
    env:
      - name: RF_CHECK_FOR
  url:
    description: "URL of your website or the host you want to ping (see monitor_type below)."
    required: False
    type: str
  expected_status_codes:
    description: "An dict of status codes you expect to receive from your website. These status codes are considered only if the monitor_type is expected_status_code."
    required: False
    type: dict
  request_headers:
    description: "An optional dict of custom HTTP headers for the request. Set the name and value properties to form a complete header."
    required: False
    type: dict
  domain_expiration:
    description: "How many days before the domain expires do you want to be alerted? Valid values are 1, 2, 3, 7, 14, 30, and 60."
    required: False
    type: int
  ssl_expiration:
    description: "How many days before the SSL certificate expires do you want to be alerted? Valid values are 1, 2, 3, 7, 14, 30, and 60."
    required: False
    type: int
  policy_id:
    description: "Set the escalation policy for the monitor"
    required: False
    type: str
  follow_redirects:
    description: "Should we automatically follow redirects when sending the HTTP request?"
    required: False
    type: bool
  monitor_type:
    description:
      - "Valid values:"
      - "status - We will check your website for 2XX HTTP status code"
      - "expected_status_code - We will check if your website returned one of the values in expected_status_codes."
      - "keyword - We will check if your website contains the required_keyword."
      - "keyword_absence - We will check if your website doesn't contain the required_keyword."
    required: False
    type: str
  required_keyword:
    description: "Required if monitor_type is set to keyword  or udp. We will create a new incident if this keyword is missing on your page."
    required: False
    type: str
  call:
    description: "Should we call the on-call person?"
    required: False
    type: bool
  sms:
    description: "Should we send an SMS to the on-call person?"
    required: False
    type: bool
  email:
    description: "Should we send an email to the on-call person?"
    required: False
    type: bool
  push:
    description: "Should we send a push notification to the on-call person?"
    required: False
    type: bool
  team_wait:
    description: "How long to wait before escalating the incident alert to the team. Leave blank to disable escalating to the entire team."
    required: False
    type: int
  paused:
    description: "Set to true to pause monitoring we won't notify you about downtime."
    required: False
    type: bool
  port:
    description:
      - "Required if monitor_type is set to tcp, udp, smtp, pop, or imap."
      - "tcp and udp monitors accept any ports, while smtp, pop, and imap accept only the specified ports corresponding with their servers (e.g. '25,465,587' for smtp)."
    required: False
    type: str
  regions:
    description: "An array of regions to set. Allowed values are ['us', 'eu', 'as', 'au'] or any subset of these regions."
    required: False
    type: list
  monitor_group_id:
    description: "Set this attribute if you want to add this monitor to a monitor group."
    required: False
    type: str
  pronounceable_name:
    description: "Pronounceable name of the monitor. We will use this when we call you. Try to make it tongue-friendly, please?"
    required: False
    type: str
  recovery_period:
    description: "How long the monitor must be up to automatically mark an incident as resolved after being down."
    required: False
    type: int
  verify_ssl:
    description: "Should we verify SSL certificate validity?"
    required: False
    type: bool
  check_frequency:
    description: "How often should we check your website? In seconds."
    required: False
    type: int
  confirmation_period:
    description: "How long should we wait after observing a failure before we start a new incident?"
    required: False
    type: int
  http_method:
    description:
      - "HTTP Method used to make a request."
      - "Valid options: GET, HEAD, POST, PUT, PATCH"
    required: False
    type: str
  request_timeout:
    description: "How long to wait before timing out the request? In seconds."
    required: False
    type: int
  request_body:
    description: "Request body for POST, PUT, PATCH requests."
    required: False
    type: str
  auth_username:
    description: "Basic HTTP authentication username to include with the request."
    required: False
    type: str
  auth_password:
    description: "Basic HTTP authentication password to include with the request."
    required: False
    type: str
    no_log: True
  maintenance_from:
    description:
      - "Start of the maintenance window each day. We won't check your website during this window."
      - "In UTC timezone. Example: '01:00:00'"
    required: False
    type: str
  maintenance_to:
    description:
      - "End of the maintenance window each day."
      - "In UTC timezone. Example: '03:00:00'"
    required: False
    type: str
  validate_certs:
    description: "Require HTTPS-webrequest certificate validation."
    required: False
    type: bool
    default: False
    env:
      - name: RF_VALIDATE_CERTS
  https_proxy:
    description: "Use a proxy for https requests during this module (will set the https_proxy ENV var)."
    required: False
    type: str
    default: None
    env:
      - name: https_proxy
      - name: HTTPS_PROXY

author:
  - Yorick Gruijthuijzen (@yorick1989)
'''

EXAMPLES = r'''
# Create / update a monitor.
- name: Create / update a monitor.
  betteruptime.betteruptime.monitors:
    api_token: <api_token>
    monitor_type: "status"
    url: "https://www.example.com"
    state: present
  register: resp

# Print the monitor information.
- name: Print the monitor information.
  debug:
    var: resp
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils.urls import open_url
from ansible_collections.betteruptime.betteruptime.plugins.module_utils.burestapi import BURestApi

import json

try:
  from urllib.parse import urlencode
except ImportError:
  from urllib import urlencode

class CustomAnsibleModule(AnsibleModule, BURestApi):

  def run(self):
    """
    Execute the module logic.
    """

    result = dict(
        changed=False,
        result={},
    )

    run_failed = False

    try:

      self.api_token=self.params['api_token']
      self.validate_certs=self.params['validate_certs'] or True
      check_for=self.params['check_for']
      state=True if self.params['state'] == 'present' else False

      data = {}

      for option in self.params:
        if self.params[option] and option not in data and option not in [ 'api_token', 'validate_certs', 'check_for', 'state' ]:
          data[option] = self.params[option]

      ret, resp = self.BUGet(
                    'monitors',
                    self.params['id'] if self.params['id'] else None
                  )

      if not ret:
        result['msg'] = resp
        run_failed = True

        return False

      matches_found = {}

      update = {}

      for entry in resp:
        for option in check_for:
          if data[option] == entry['attributes'][option]:
            matches_found.update({ option: entry['attributes'][option] })

        if len(matches_found) == len(check_for):
          id = entry['id']
          result['result'] = entry['attributes']
          for option in data.keys():
            if data[option] != entry['attributes'][option]:
              update[option] = data[option]
          break

      if 'id' in locals() and len(update) == 0 and not state:

        resp = self.httpRequest(
          'https://betteruptime.com/api/v2/monitors/' + str(id),
          {
            'Authorization': 'Bearer {}'.format( self.api_token ),
            'Content-Type': 'application/json'
          },
          data,
          'DELETE'
        )

        result['return_code'] = resp.code

        if result['return_code'] == 204:
          result['result'] = {}

          result['changed'] = True

      elif len(update) > 0 and state:

        result['statetest'] = state

        resp = self.httpRequest(
          'https://betteruptime.com/api/v2/monitors/' + str(id),
          {
            'Authorization': 'Bearer {}'.format( self.api_token ),
            'Content-Type': 'application/json'
          },
          data,
          'PATCH'
        )

        result['result'] = json.loads(resp.read())

        result['return_code'] = resp.code

        if result['return_code'] == 200:
          result['changed'] = True

      elif len(result['result']) == 0 and state:

        resp = self.httpRequest(
          'https://betteruptime.com/api/v2/monitors',
          {
            'Authorization': 'Bearer {}'.format( self.api_token ),
            'Content-Type': 'application/json'
          },
          data,
          'POST'
        )

        result['result'] = json.loads(resp.read())

        result['return_code'] = resp.code

        if result['return_code'] == 201:
          result['changed'] = True

      if 'errors' in result['result']:
        result['msg'] = 'Task failed.'
        run_failed = True
        result['changed'] = False

    except:
      raise

    if self.check_mode:
      self.exit_json(**result)

    if run_failed:
      self.fail_json(**result)
    else:
      self.exit_json(**result)

def main():

  CustomAnsibleModule(
    argument_spec=dict(
      api_token=dict(
        type='str',
        required=True,
        fallback=(env_fallback, ['BU_API_TOKEN'])
      ),
      state=dict(
        type='str',
        required=False,
        choices=['present','absent'],
        default='present',
        fallback=(env_fallback, ['BU_STATE'])
      ),
      id=dict(
        type='int',
        required=False,
        fallback=(env_fallback, ['BU_ID'])
      ),
      check_for=dict(
        type='list',
        required=False,
        default='url',
        fallback=(env_fallback, ['BU_check_for'])
      ),
      url=dict(
        type='str',
        required=False
      ),
      expected_status_codes=dict(
        type='dict',
        required=False
      ),
      request_headers=dict(
        type='dict',
        required=False
      ),
      domain_expiration=dict(
        type='int',
        required=False
      ),
      ssl_expiration=dict(
        type='int',
        required=False
      ),
      policy_id=dict(
        type='str',
        required=False
      ),
      follow_redirects=dict(
        type='bool',
        required=False
      ),
      monitor_type=dict(
        type='str',
        required=False,
        choices=['status', 'expected_status_code', 'keyword', 'keyword_absence']
      ),
      required_keyword=dict(
        type='str',
        required=False
      ),
      call=dict(
        type='bool',
        required=False
      ),
      sms=dict(
        type='bool',
        required=False
      ),
      email=dict(
        type='bool',
        required=False
      ),
      push=dict(
        type='bool',
        required=False
      ),
      team_wait=dict(
        type='int',
        required=False
      ),
      paused=dict(
        type='bool',
        required=False
      ),
      port=dict(
        type='str',
        required=False
      ),
      regions=dict(
        type='list',
        required=False,
        choices=['us', 'eu', 'as', 'au']
      ),
      monitor_group_id=dict(
        type='str',
        required=False
      ),
      pronounceable_name=dict(
        type='str',
        required=False
      ),
      recovery_period=dict(
        type='int',
        required=False
      ),
      verify_ssl=dict(
        type='bool',
        required=False
      ),
      check_frequency=dict(
        type='int',
        required=False
      ),
      confirmation_period=dict(
        type='int',
        required=False
      ),
      http_method=dict(
        type='str',
        required=False,
        choices=['GET', 'HEAD', 'POST', 'PUT', 'PATCH']
      ),
      request_timeout=dict(
        type='int',
        required=False
      ),
      request_body=dict(
        type='str',
        required=False
      ),
      auth_username=dict(
        type='str',
        required=False
      ),
      auth_password=dict(
        type='str',
        required=False
      ),
      maintenance_from=dict(
        type='str',
        required=False
      ),
      maintenance_to=dict(
        type='str',
        required=False
      ),
      validate_certs=dict(
        type='bool',
        required=False,
        default=False, fallback=(env_fallback, ['BU_VALIDATE_CERTS'])
      ),
      https_proxy=dict(
        type='str',
        required=False,
        default=None,
        fallback=(env_fallback, ['https_proxy','HTTPS_PROXY'])
      )
    ),
    required_together=[
      ('url', 'monitor_type'),
    ],
    required_one_of=[
      ('id', 'url'),
    ],
    supports_check_mode=True
  ).run()

if __name__ == '__main__':
  main()
