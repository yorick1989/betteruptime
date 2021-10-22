#!/usr/bin/python

# Copyright: (c) 2021, Yorick Gruijthuijzen <yorick@gruijthuijzen.nl>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: status_page

short_description: "This module creates / updates or removes a status page on / from Better Uptime."

version_added: "1.0.0"

description: "This module creates / updates or removes a status page on / from Better Uptime."

options:
  api_token:
    description: "API Bearer token."
    required: True
    type: str
    no_log: True
    env:
      - name: BU_API_TOKEN
  state:
    description: "The state of the record (choices: present (default) and absent)."
    required: False
    type: str
    default: present
    env:
      - name: BU_STATE
  id:
    description: "The ID of the status page you want to update"
    required: False
    type: int
    env:
      - name: BU_ID
  check_for:
    description:
      - "Provide a str or list of options to compare existing items with."
      - "Overwrite / update when all the options do match and if it doesn't; a new item will be created."
      - "default: subdomain"
    required: False
    type: list
    default: subdomain
    env:
      - name: RF_CHECK_FOR
  history:
    description:
      - "Number of days to display on the status page."
      - "Minimum 90 days."
    required: False
    type: str
    env:
      - name: BU_HISTORY
  company_name:
    description: "Name of your company."
    required: False
    type: str
    env:
      - name: BU_COMPANY_NAME
  company_url:
    description: "URL of your company's website."
    required: False
    type: str
    env:
      - name: RF_COMPANY_URL
  contact_url:
    description: "URL that should be used for contacting you in case of an emergency."
    required: False
    type: str
    env:
      - name: BU_CONTACT_URL
  logo_url:
    description:
      - "A direct link to your company's logo."
      - "The image should be under 20MB in size."
    required: False
    type: str
    env:
      - name: BU_LOGO_URL
  timezone:
    description:
      - "What timezone should we display your status page in?"
      - "The accepted values can be found in the Rails TimeZone documentation. https://api.rubyonrails.org/classes/ActiveSupport/TimeZone.html."
    required: False
    type: str
    env:
      - name: BU_TIMEZONE
  subdomain:
    description:
      - "What subdomain should we use for your status page?"
      - "This needs to be unique across our entire application, so choose carefully."
    required: False
    type: str
    env:
      - name: BU_SUBDOMAIN
  custom_domain:
    description: "Do you want a custom domain on your status page?"
    required: False
    type: str
    env:
      - name: BU_CUSTOM_DOMAIN
  hide_from_search_engines:
    description: "Hide your status page from search engines."
    required: False
    type: bool
    env:
      - name: BU_HIDE_FROM_SEARCH_ENGINES
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
  - "Yorick Gruijthuijzen (@yorick1989)"
'''

EXAMPLES = r'''
# Create / update a status page.
- name: Create / update a status page.
  betteruptime.betteruptime.status_page:
    api_token: <api_token>
    company_name: "ACME"
    company_url: "example.com"
    timezone: "UTC"
    subdomain: "status"
  register: resp

# Print the status page information.
- name: Print the status page information.
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
                    'status-pages',
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
          'https://betteruptime.com/api/v2/status-pages/' + str(id),
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
          'https://betteruptime.com/api/v2/status-pages/' + str(id),
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
          'https://betteruptime.com/api/v2/status-pages',
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
        default='subdomain',
        fallback=(env_fallback, ['BU_CHECK_FOR'])
      ),
      history=dict(
        type='int',
        required=False,
        fallback=(env_fallback, ['BU_HISTORY'])
      ),
      company_name=dict(
        type='str',
        required=False,
        fallback=(env_fallback, ['BU_COMPANY_NAME'])
      ),
      company_url=dict(
        type='str',
        required=False,
        fallback=(env_fallback, ['BU_COMPANY_URL'])
      ),
      contact_url=dict(
        type='str',
        required=False,
        fallback=(env_fallback, ['BU_CONTACT_URL'])
      ),
      logo_url=dict(
        type='str',
        required=False,
        fallback=(env_fallback, ['BU_LOGO_URL'])
      ),
      timezone=dict(
        type='str',
        required=False,
        fallback=(env_fallback, ['BU_TIMEZONE'])
      ),
      subdomain=dict(
        type='str',
        required=False,
        fallback=(env_fallback, ['BU_SUBDOMAIN'])
      ),
      custom_domain=dict(
        type='str',
        required=False,
        fallback=(env_fallback, ['BU_CUSTOM_DOMAIN'])
      ),
      hide_from_search_engines=dict(
        type='bool',
        required=False,
        fallback=(env_fallback, ['BU_HIDE_FROM_SEARCH_ENGINES'])
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
      ('company_name', 'company_url', 'timezone', 'subdomain'),
    ],
    required_one_of=[
      ('id', 'subdomain'),
    ],
    supports_check_mode=True
  ).run()

if __name__ == '__main__':
  main()
