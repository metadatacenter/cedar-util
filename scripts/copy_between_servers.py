#!/usr/bin/python

# Created:      Oct-31-2016
# Last updated: Aug-30-2017
# copy_between_servers.py: Utility to copy resources (templates, elements, and template instances) between
# different CEDAR servers.
# 
# - All resource ids are regenerated
# - Ids of elements embedded into templates are not modified

import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import os.path
import sys
import jsclean
import time
from datetime import datetime
import json
import urllib

# Server uris
source_server = "https://resource.staging.metadatacenter.net/"
target_server = "https://resource.metadatacenter.net/"
# Api keys
source_api_key = "<apiKey1>"
target_api_key = "<apiKey2>"

# Folder ids
target_folder_id_templates = "https://repo.metadatacenter.net/folders/f5729337-6cb8-4b3c-98a4-4d39ea481bb3"
target_folder_id_instances = "https://repo.metadatacenter.net/folders/f5729337-6cb8-4b3c-98a4-4d39ea481bb3"
target_folder_id_elements = "https://repo.metadatacenter.net/folders/f5729337-6cb8-4b3c-98a4-4d39ea481bb3"

# Ids of the resources to be copied
source_templates_ids = ["https://repo.staging.metadatacenter.net/templates/44018509-4aa3-40aa-9041-77b2f89c04ec",
                        "https://repo.staging.metadatacenter.net/templates/fe51b2c3-4144-4be0-a069-9346227622e6"]
source_elements_ids = ["https://repo.staging.metadatacenter.net/template-elements/ae325dd7-bb4b-40a3-b730-58c855931a1b",
                       "https://repo.staging.metadatacenter.net/template-elements/19a7df21-7608-49e3-a002-d488cecb1dc2"]

# Replacements to be done in all the resources copied
old = "staging.metadatacenter.net"
new = "metadatacenter.net"

limit_per_call = 500
# Max number of instances to be created
max_count = 40000


def main():
    # Disable InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Move templates and instances
    for source_template_id in source_templates_ids:
        template_text = get_template(source_server, source_template_id, source_api_key)
        template_text = template_text.replace(old, new)
        template_json = json.loads(template_text)
        target_template_json = post_template(target_server, template_json, target_folder_id_templates, target_api_key)
        target_template_id = target_template_json['@id']
        post_instances(source_server, target_server, source_template_id, target_template_id, target_folder_id_instances,
                       max_count, limit_per_call, source_api_key, target_api_key)

    # Move elements
    for source_element_id in source_elements_ids:
        element_text = get_element(source_server, source_element_id, source_api_key)
        element_text = element_text.replace(old, new)
        element_json = json.loads(element_text)
        post_element(target_server, element_json, target_folder_id_elements, target_api_key)

    print("**** Done ****")


# Used to delete the template and instances created
# def main():  
#     # Disable InsecureRequestWarning
#     requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  
#     templ_id = "https://repo.metadatacenter.orgx/templates/cd292507-4a49-4326-8196-d262255c3507"
#     delete_instances(target_server, templ_id, max_count, limit_per_call, target_api_key)
#     print("**** Done ****")

def get_template(server, template_id, api_key):
    url = server + "templates/" + urllib.parse.quote(template_id, safe='')
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    response = requests.request("GET", url, headers=headers)
    print("GET template response: " + str(response.status_code))
    return response.text


def get_element(server, element_id, api_key):
    url = server + "template-elements/" + urllib.parse.quote(element_id, safe='')
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    response = requests.request("GET", url, headers=headers)
    print("GET element response: " + str(response.status_code))
    return response.text


def get_instance(server, instance_id, api_key):
    url = server + "template-instances/" + urllib.parse.quote(instance_id, safe='')
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    # print("GET instance response: " + str(response.status_code))
    return response.text


def delete_instance(server, instance_id, api_key):
    url = server + "template-instances/" + urllib.parse.quote(instance_id, safe='')
    print(url)
    headers = {
        'authorization': "apiKey " + api_key
    }
    response = requests.request("DELETE", url, headers=headers, verify=False)
    print("DELETE instance response: " + str(response.status_code))


def delete_template(server, template_id, api_key):
    url = server + "templates/" + urllib.parse.quote(template_id, safe='')
    print(url)
    headers = {
        'authorization': "apiKey " + api_key
    }
    response = requests.request("DELETE", url, headers=headers, verify=False)
    print("DELETE template response: " + str(response.status_code))


def post_template(server, template, folder_id, api_key):
    # Delete @id field if it exists
    del template['@id']
    # template = json.dumps(template_json)
    url = server + "templates"
    querystring = {"folder_id": folder_id}
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    response = requests.request("POST", url, json=template, headers=headers, params=querystring, verify=False)
    print("POST template response: " + str(response.status_code))
    # print("POST template response: " + str(response.text))
    return json.loads(response.text)


def post_element(server, element, folder_id, api_key):
    # Delete @id field if it exists
    del element['@id']
    url = server + "template-elements"
    querystring = {"folder_id": folder_id}
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    response = requests.request("POST", url, json=element, headers=headers, params=querystring, verify=False)
    print("POST element response: " + str(response.status_code))
    # print("POST template response: " + str(response.text))
    return json.loads(response.text)


def get_template_instances_summary(server, template_id, max_count, limit_per_call, api_key):
    print('*** Getting instance summaries ***')
    print('    server: ' + server)
    print('    template_id: ' + template_id)
    print('    max_count: ' + str(max_count))
    print('    limit_per_call: ' + str(limit_per_call))
    instances_summary = []
    # Retrieve basic info for instances
    url_source_search = server + "search-deep"
    offset = 0
    if max_count <= limit_per_call:
        limit_param = max_count
    else:
        limit_param = limit_per_call
    finished = False
    while not finished:
        # print('------------')
        # print('  offset = ' + str(offset))
        # print('  limit_param = ' + str(limit_param))
        # print('------------')

        querystring = {"derived_from_id": template_id, "q": "*", "limit": limit_param, "offset": offset}
        headers = {
            'content-type': "application/json",
            'authorization': "apiKey " + api_key
        }
        response_instances_summary = requests.request("GET", url_source_search, headers=headers, params=querystring,
                                                      verify=False)
        print("    GET instances summary URL: " + str(response_instances_summary.url))
        print("    GET instances summary response: " + str(response_instances_summary.status_code))
        response_json = json.loads(response_instances_summary.text)
        total_count = response_json['totalCount']
        instances_summary.extend(response_json["resources"])

        offset = offset + limit_param

        if not len(response_json["resources"]):
            finished = True

        if (offset + limit_param) > max_count:
            if (offset < max_count):
                limit_param = max_count - offset
            else:
                finished = True

    print('    Total number of instance summaries retrieved: ' + str(len(instances_summary)))
    return instances_summary


def get_template_instances(server, template_id, max_count, limit_per_call, api_key):
    instances_summary = get_template_instances_summary(server, template_id, max_count, limit_per_call, api_key)
    instances = []
    for summary in instances_summary:
        # Retrieve instance
        instance = get_instance(source_server, summary['@id'], source_api_key)
        instances.append(instance)
    return instances


def post_instances(source_server, target_server, source_template_id, target_template_id, target_folder_id, max_count,
                   limit_per_call, source_api_key, target_api_key):
    instances_summary = get_template_instances_summary(source_server, source_template_id, max_count, limit_per_call,
                                                       source_api_key)
    url_target_instances = target_server + "template-instances"
    print('Retrieving full instances and posting them to the target system')
    total_count = len(instances_summary)
    count = 0
    for ins in instances_summary:
        instance_text = get_instance(source_server, ins['@id'], source_api_key)
        instance_text = instance_text.replace(old, new)
        instance = json.loads(instance_text)
        del instance['@id']
        instance['schema:isBasedOn'] = target_template_id
        querystring = {"folder_id": target_folder_id}
        headers = {
            'content-type': "application/json",
            'authorization': "apiKey " + target_api_key
        }
        response = requests.request("POST", url_target_instances, json=instance, headers=headers, params=querystring,
                                    verify=False)
        # print("POST instance response: " + str(response.status_code))
        print("Posted instance no. " + str(count) + " (" + str(float((100 * count) / total_count)) + "%)")
        count = count + 1


def delete_instances(server, template_id, max_count, limit_per_call, api_key):
    print('*** Removing instances ***')
    print('    server: ' + server);
    print('    template_id: ' + template_id);

    instances_json = get_template_instances_summary(server, template_id, max_count, limit_per_call, api_key)
    for instance in instances_json:
        delete_instance(server, instance['@id'], api_key)


if __name__ == "__main__":
    main()
