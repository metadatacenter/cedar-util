# -*- coding: utf-8 -*-

"""
utils.validator
~~~~~~~~~~~~~~
This module provides utility functions that are used to validate a CEDAR
resource (template/element/instance). The function will return the validation
status followed by the validation message
"""

import requests
import json
from . import to_boolean
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def validate_resource(api_key, request_url, resource):
    response = send_post_request(api_key, request_url, resource)
    if response.status_code == requests.codes.ok:
        message = json.loads(response.text)
        return to_boolean(message["validates"]), message
    else:
        response.raise_for_status()


def validate_template(server_address, api_key, template):
    request_url = server_address + "/command/validate?resource_type=template"
    return validate_resource(api_key, request_url, template)


def validate_element(server_address, api_key, element):
    request_url = server_address + "/command/validate?resource_type=element"
    return validate_resource(api_key, request_url, element)


def validate_field(server_address, api_key, field):
    request_url = server_address + "/command/validate?resource_type=field"
    return validate_resource(api_key, request_url, field)


def validate_instance(server_address, api_key, instance):
    request_url = server_address + "/command/validate?resource_type=instance"
    return validate_resource(api_key, request_url, instance)


def send_post_request(api_key, request_url, data):
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }
    response = requests.request("POST", request_url, headers=headers, data=json.dumps(data), verify=False)
    return response