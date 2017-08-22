import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def store_resource(api_key, request_url, resource):
    response = send_post_request(api_key, request_url, resource)
    if response.status_code == requests.codes.ok:
        document = json.loads(response.text)
        return document
    else:
        response.raise_for_status()


def store_template(server_address, api_key, template, override=False):
    request_url = server_address + "/templates?import_mode=" + str(override)
    return store_resource(api_key, request_url, template)


def store_element(server_address, api_key, element, override=False):
    request_url = server_address + "/template-elements?import_mode=" + str(override)
    return store_resource(api_key, request_url, element)


def store_instance(server_address, api_key, instance, override=False):
    request_url = server_address + "/template-instances?import_mode=" + str(override)
    return store_resource(api_key, request_url, instance)


def send_post_request(api_key, request_url, resource):
    headers = {
        'Content-Type': "application/json",
        'Authorization': api_key
    }
    response = requests.request("POST", request_url, json=resource, headers=headers, verify=False)
    return response
