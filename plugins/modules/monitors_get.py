#!/usr/bin/python

# Copyright: (c) 2021, Yorick Gruijthuijzen <yorick@gruijthuijzen.nl>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: betteruptime_monitors_get

short_description: "This module pulls all the available status pages from Better Uptime."

version_added: "1.0.0"

description: "This module pulls all the available status pages from Better Uptime."

options:
  api_token:
    description: "API Bearer token."
    required: True
    type: str
    no_log: True
    env:
      - name: BU_API_TOKEN
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
# Get all the available monitors.
- name: Get all the available monitors.
  betteruptime.betteruptime.monitors_get:
    api_token: <api_token>
  register: resp

# Print all the available monitors.
- name: Print all the available monitors.
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

      resp = self.httpRequest(
        'https://betteruptime.com/api/v2/monitors',
        {
          'Authorization': 'Bearer {}'.format( self.api_token ),
          'Content-Type': 'application/json'
        }
      )

      result['result'] = json.loads(resp.read())

      result['return_code'] = resp.code

      if result['return_code'] == 201:
        result['changed'] = True

      if 'errors' in result['result']:
        result['msg'] = 'Task failed.'
        run_failed = True
        result['changed'] = False
      else:
        result['result'] = result['result']['data']

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
    supports_check_mode=True
  ).run()

if __name__ == '__main__':
  main()
