#!/usr/bin/python

# Copyright: (c) 2021, Yorick Gruijthuijzen <yorick@gruijthuijzen.nl>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.urls import open_url

import json

try:
  from urllib.parse import urlencode
except ImportError:
  from urllib import urlencode

class BURestApi():

  use_proxy       = False
  validate_certs  = True

  def httpRequest(self, url, headers=None, data=None, method='GET'):
    """
    Execute a http webrequest.

    :param str url: The url of your http request.
    :param dict headers: The headers of your http request (Default: None).
    :param str/dict data: The data of your http request (Default: None).
    :param str method: The method of your http request (Default: GET).
    """

    if data != None and not isinstance(data,dict):
      data = bytearray(data, 'utf8')
    elif isinstance(data,dict):
      data = json.dumps(data)

    try:
      resp = open_url(
        url,
        method=method,
        data=data,
        headers=headers,
        validate_certs=self.validate_certs,
        use_proxy=self.use_proxy
      )
    except Exception as r:
      resp = r

    return resp


  def BUGet(self, resource, id=None):
    """
    Get a list of all the added betteruptime of a specific resource or pull one specifically by providing the id.

    :param str resource: The Betteruptime resource type.
    :param int id: The resource id (Default: None).
    """

    url = 'https://betteruptime.com/api/v2/' + resource + (('/' + str(id)) if id else '')

    response = {
      'resp' : dict(),
      'code' : int()
    }

    while True:

      resp = self.httpRequest(
        url,
        {
          'Authorization': 'Bearer {}'.format( self.api_token ),
          'Content-Type': 'application/json'
        }
      )

      response['resp'].update(json.loads(resp.read()))

      response['code'] = resp.code

      if 'data' not in response['resp'] or 'pagination' not in response['resp']['data'] or response['resp']['data']['pagination']['next'] == 'null':
        break
      elif 'data' in response['resp'] and 'pagination' in response['resp']['data'] and response['resp']['data']['pagination']['next'] != 'null':
        url = response['resp']['data']['pagination']['next']

    if 'errors' in response['resp']:
      return (False, response['resp']['errors'])
    else:
      return (True, response['resp']['data'])
