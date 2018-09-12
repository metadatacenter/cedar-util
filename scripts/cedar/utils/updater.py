# -*- coding: utf-8 -*-

"""
utils.updater
~~~~~~~~~~~~~~
This module provides utility functions that are used to modify a CEDAR
resource (template/element/instance) via a PUT request.
"""

import requests
import json
from urllib.parse import quote
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def update_resource(api_key, request_url, resource):
    response = send_put_request(api_key, request_url, resource)
    if response.status_code == requests.codes.ok:
        document = json.loads(response.text)
        return document
    else:
        response.raise_for_status()


def update_template(server_address, api_key, template_id, template):
    request_url = server_address + "/templates/" + escape(template_id)
    return update_resource(api_key, request_url, template)


def update_element(server_address, api_key, element_id, element):
    request_url = server_address + "/template-elements/" + escape(element_id)
    return update_resource(api_key, request_url, element)


def update_instance(server_address, api_key, instance_id, instance):
    request_url = server_address + "/template-instances/" + escape(instance_id)
    return update_resource(api_key, request_url, instance)


def update_template_permission(server_address, api_key, instance_id, permission):
    request_url = server_address + "/templates/" + escape(instance_id) + "/permissions"
    return update_resource(api_key, request_url, permission)


def update_element_permission(server_address, api_key, instance_id, permission):
    request_url = server_address + "/template-elements/" + escape(instance_id) + "/permissions"
    return update_resource(api_key, request_url, permission)


def update_field_permission(server_address, api_key, instance_id, permission):
    request_url = server_address + "/template-fields/" + escape(instance_id) + "/permissions"
    return update_resource(api_key, request_url, permission)


def update_instance_permission(server_address, api_key, instance_id, permission):
    request_url = server_address + "/template-instances/" + escape(instance_id) + "/permissions"
    return update_resource(api_key, request_url, permission)


def send_put_request(api_key, request_url, resource):
    headers = {
        'Content-Type': "application/json",
        'Authorization': api_key
    }
    response = requests.request("PUT", request_url, json=resource, headers=headers, verify=False)
    return response


def escape(s):
    return quote(str(s), safe='')
