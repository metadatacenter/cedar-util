import requests
import json
from uritemplate import expand
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_resource(api_key, request_url):
    response = send_get_request(api_key, request_url)
    if response.status_code == requests.codes.ok:
        document = json.loads(response.text)
        return document
    else:
        response.raise_for_status()


def get_template(api_key, url_template=None, **kwargs):
    if url_template is None:
        url_template = 'https://resource.metadatacenter.orgx/templates{/template_id}'
    request_url = expand(url_template, kwargs)
    return send_get_request(api_key, request_url)


def get_element(api_key, url_template=None, **kwargs):
    if url_template is None:
        url_template = 'https://resource.metadatacenter.orgx/template-elements{/element_id}'
    request_url = expand(url_template, kwargs)
    return send_get_request(api_key, request_url)


def get_instance(api_key, url_template=None, **kwargs):
    if url_template is None:
        url_template = 'https://resource.metadatacenter.orgx/template-instances{/instance_id}'
    request_url = expand(url_template, kwargs)
    return send_get_request(api_key, request_url)


def send_get_request(api_key, request_url):
    headers = {
        'Content-Type': "application/json",
        'Authorization': api_key
    }
    response = requests.request("GET", request_url, headers=headers, verify=False)
    return response
