import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def validate_template(api_key, document, request_url=None):
    if request_url is None:
        request_url = "https://resource.metadatacenter.orgx/command/validate?resource_type=template"
    return send_post_request(api_key, request_url, document)


def validate_instance(api_key, document, request_url=None):
    if request_url is None:
        request_url = "https://resource.metadatacenter.orgx/command/validate?resource_type=instance"
    return send_post_request(api_key, request_url, document)


def validate_element(api_key, document, request_url=None):
    if request_url is None:
        request_url = "https://resource.metadatacenter.orgx/command/validate?resource_type=element"
    return send_post_request(api_key, request_url, document)


def send_post_request(api_key, request_url, data):
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }
    response = requests.request("POST", request_url, headers=headers, data=json.dumps(data), verify=False)
    message = json.loads(response.text)
    return response.status_code, message