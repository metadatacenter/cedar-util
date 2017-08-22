# -*- coding: utf-8 -*-

"""
utils.remover
~~~~~~~~~~~~~~
This module provides utility functions that are used to remove a CEDAR
resource (template/element/instance) via a DELETE request.
"""

import requests
import json
from urllib.parse import quote
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def remove_resource(api_key, request_url):
    response = send_delete_request(api_key, request_url)
    if response.status_code == requests.codes.ok:
        document = json.loads(response.text)
        return document
    else:
        response.raise_for_status()


def remove_template(server_address, api_key, template_id):
    request_url = server_address + "/templates/" + escape(template_id)
    return remove_resource(api_key, request_url)


def remove_element(server_address, api_key, element_id):
    request_url = server_address + "/template-elements/" + escape(element_id)
    return remove_resource(api_key, request_url)


def remove_instance(server_address, api_key, instance_id):
    request_url = server_address + "/template-instances/" + escape(instance_id)
    return remove_resource(api_key, request_url)


def send_delete_request(api_key, request_url):
    headers = {
        'Content-Type': "application/json",
        'Authorization': api_key
    }
    response = requests.request("DELETE", request_url, headers=headers, verify=False)
    return response


def escape(s):
    return quote(str(s), safe='')
