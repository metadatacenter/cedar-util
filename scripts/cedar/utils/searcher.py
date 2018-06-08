# -*- coding: utf-8 -*-

"""
utils.searcher
~~~~~~~~~~~~~~
This module provides utility functions that are used to search a CEDAR
resource (template/element/instance) by specifying the keyword query and
some other search parameters (e.g., max_count and limit).

If the user doesn't specify the keyword query then the function will
return all the items (perform a "search all" call)
"""

import math
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def search_resources(api_key, request_url, max_count=None, limit_per_page=500):
    total_count = max_count
    if max_count is None:
        total_count = get_total_count(api_key, request_url)

    total_page = get_total_paging(total_count, limit_per_page)

    query_limit = limit_per_page
    if total_count < limit_per_page:
        query_limit = total_count

    offset = 0
    result_list = []
    for page in range(1, total_page + 1):
        search_result = do_search(api_key, request_url, offset, query_limit)
        result_list.extend(get_identifiers(search_result))
        offset = limit_per_page * page
    return result_list


def search_templates(server_address, api_key, query='*', max_count=None, limit_per_page=500):
    request_url = server_address + "/search?q=" + query + "&resource_types=template"
    return search_resources(api_key, request_url, max_count, limit_per_page)


def search_elements(server_address, api_key, query='*', max_count=None, limit_per_page=500):
    request_url = server_address + "/search?q=" + query + "&resource_types=element"
    return search_resources(api_key, request_url, max_count, limit_per_page)


def search_instances(server_address, api_key, query='*', max_count=None, limit_per_page=500):
    request_url = server_address + "/search?q=" + query + "&resource_types=instance"
    return search_resources(api_key, request_url, max_count, limit_per_page)


def search_instances_of(server_address, api_key, template_id, max_count=None, limit_per_page=500):
    request_url = server_address + "/search-deep?is_based_on=" + template_id
    return search_resources(api_key, request_url, max_count, limit_per_page)


def get_total_paging(total_count, limit_per_page):
    return math.ceil(total_count/limit_per_page)


def get_total_count(api_key, request_url):
    search_result = do_search(api_key, request_url, 0, 100)
    total_count = search_result["totalCount"]
    return total_count


def get_identifiers(search_result):
    identifiers = []
    if "resources" in search_result:
        for resource in search_result["resources"]:
            identifiers.append(resource["@id"])
    return identifiers


def do_search(api_key, base_url, offset, limit):
    request_url = base_url + "&offset=" + str(offset) + "&limit=" + str(limit)
    return send_get_request(api_key, request_url)


def send_get_request(api_key, request_url):
    headers = {
        'Content-Type': "application/json",
        'Authorization': api_key
    }
    response = requests.request("GET", request_url, headers=headers, verify=False)
    document = json.loads(response.text)
    return document
