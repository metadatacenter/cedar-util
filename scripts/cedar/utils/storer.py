# -*- coding: utf-8 -*-

"""
utils.storer
~~~~~~~~~~~~~~
This module provides utility functions that are used to create a CEDAR
resource (template/element/instance) via a POST request.
"""

import requests
import json
from urllib.parse import quote
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def store_resource(api_key, request_url, resource):
    response = send_post_request(api_key, request_url, resource)
    if response.status_code == requests.codes.ok:
        document = json.loads(response.text)
        return document
    else:
        response.raise_for_status()


def store_template(server_address, api_key, template, folder_id):
    request_url = server_address + "/templates?folder_id=" + escape(folder_id)
    return store_resource(api_key, request_url, template)


def store_element(server_address, api_key, element, folder_id):
    request_url = server_address + "/template-elements?folder_id=" + escape(folder_id)
    return store_resource(api_key, request_url, element)


def store_field(server_address, api_key, field, folder_id):
    request_url = server_address + "/template-fields?folder_id=" + escape(folder_id)
    return store_resource(api_key, request_url, field)


def store_instance(server_address, api_key, instance, folder_id):
    request_url = server_address + "/template-instances?folder_id=" + escape(folder_id)
    return store_resource(api_key, request_url, instance)


def send_post_request(api_key, request_url, resource):
    headers = {
        'Content-Type': "application/json",
        'Authorization': api_key
    }
    response = requests.request("POST", request_url, json=resource, headers=headers, verify=False)
    return response


def escape(s):
    return quote(str(s), safe='')