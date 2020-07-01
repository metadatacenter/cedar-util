# -*- coding: utf-8 -*-

"""
utils.getter
~~~~~~~~~~~~~~
This module provides utility functions that are used to get a CEDAR
resource (template/element/instance) via a GET request.
"""

import requests
import json
from urllib.parse import quote
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_resource(api_key, request_url):
    response = send_get_request(api_key, request_url)
    if response.status_code == requests.codes.ok:
        document = json.loads(response.text)
        return document
    else:
        response.raise_for_status()


def get_template(server_address, api_key, template_id):
    request_url = server_address + "/templates/" + escape(template_id)
    return get_resource(api_key, request_url)


def get_element(server_address, api_key, element_id):
    request_url = server_address + "/template-elements/" + escape(element_id)
    return get_resource(api_key, request_url)


def get_field(server_address, api_key, field_id):
    request_url = server_address + "/template-fields/" + escape(field_id)
    return get_resource(api_key, request_url)


def get_instance(server_address, api_key, instance_id):
    request_url = server_address + "/template-instances/" + escape(instance_id)
    return get_resource(api_key, request_url)


def get_template_permissions(server_address, api_key, template_id):
    request_url = server_address + "/templates/" + escape(template_id) + "/permissions"
    return get_resource(api_key, request_url)


def get_element_permissions(server_address, api_key, element_id):
    request_url = server_address + "/template-elements/" + escape(element_id) + "/permissions"
    return get_resource(api_key, request_url)


def get_field_permissions(server_address, api_key, field_id):
    request_url = server_address + "/template-fields/" + escape(field_id) + "/permissions"
    return get_resource(api_key, request_url)


def get_instance_permissions(server_address, api_key, instance_id):
    request_url = server_address + "/template-instances/" + escape(instance_id) + "/permissions"
    return get_resource(api_key, request_url)


def send_get_request(api_key, request_url):
    headers = {
        'Content-Type': "application/json",
        'Authorization': api_key
    }
    response = requests.request("GET", request_url, headers=headers, verify=False)
    return response


def escape(s):
    return quote(str(s), safe='')
