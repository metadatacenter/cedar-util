import math
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def all_templates(api_key, request_url=None, max_count=None, limit_per_page=500):
    if request_url is None:
        request_url = "https://resource.metadatacenter.orgx/search?q=*&resource_types=template"

    total_count = max_count
    if max_count is None:
        total_count = get_total_count(api_key, request_url)

    total_page = get_total_paging(total_count, limit_per_page)

    offset = 0
    template_list = []
    for page in range(1, total_page + 1):
        template_details = get_details(api_key, request_url, offset, limit_per_page)
        template_list.extend(get_identifier_list(template_details))
        offset = limit_per_page * page
    return template_list


def all_elements(api_key, request_url=None, max_count=None, limit_per_page=500):
    if request_url is None:
        request_url = "https://resource.metadatacenter.orgx/search?q=*&resource_types=element"

    total_count = max_count
    if max_count is None:
        total_count = get_total_count(api_key, request_url)

    total_page = get_total_paging(total_count, limit_per_page)

    offset = 0
    template_list = []
    for page in range(1, total_page + 1):
        template_details = get_details(api_key, request_url, offset, limit_per_page)
        template_list.extend(get_identifier_list(template_details))
        offset = limit_per_page * page
    return template_list


def all_instances(api_key, request_url=None, max_count=None, limit_per_page=500):
    if request_url is None:
        request_url = "https://resource.metadatacenter.orgx/search?q=*&resource_types=instance"

    total_count = max_count
    if max_count is None:
        total_count = get_total_count(api_key, request_url)

    total_page = get_total_paging(total_count, limit_per_page)

    offset = 0
    template_list = []
    for page in range(1, total_page + 1):
        template_details = get_details(api_key, request_url, offset, limit_per_page)
        template_list.extend(get_identifier_list(template_details))
        offset = limit_per_page * page
    return template_list


def get_total_paging(total_count, limit_per_page):
    return math.ceil(total_count/limit_per_page)


def get_total_count(api_key, request_url):
    template_details = get_details(api_key, request_url, 0, 1)
    total_count = template_details["totalCount"]
    return total_count


def get_details(api_key, base_url, offset, limit):
    request_url = base_url + "&offset=" + str(offset) + "&limit=" + str(limit)
    return send_get_request(api_key, request_url)


def get_identifier_list(details):
    identifier_list = []
    for resource in details["resources"]:
        identifier_list.append(resource["@id"])
    return identifier_list


def send_get_request(api_key, request_url):
    headers = {
        'Content-Type': "application/json",
        'Authorization': api_key
    }
    response = requests.request("GET", request_url, headers=headers, verify=False)
    document = json.loads(response.text)
    return document