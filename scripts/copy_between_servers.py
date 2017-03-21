#!/usr/bin/python

# Created:      Oct-31-2016
# Last updated: Mar-1-2017
# copy_between_servers.py: Utility to copy resources between different CEDAR servers.
# 
# - It is currently limited to copy a template and, optionally, all its instances 
#       1) Downloads the template from the source server
#       2) Uploads the template to the target server
#       3) Optionally, downloads all the template instances from the source server
#       4) Optionally, uploads the instances to the target server
# - Both the template id and the instances ids are regenerated

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

source_server = "https://resource.staging.metadatacenter.net/"
target_server = "https://resource.metadatacenter.orgx/"
source_api_key = "<YourApiKey>"
target_api_key = "<YourApiKey>"
target_folder_id_template = "https://repo.metadatacenter.orgx/folders/49ea90c8-8fa8-444c-bf86-b0914fbf5f1b"
target_folder_id_instances = "https://repo.metadatacenter.orgx/folders/9ae00f39-a6f4-4a88-8977-9f4117955f32"
source_template_id = "https://repo.staging.metadatacenter.net/templates/99de8dbb-5e26-4b31-928e-903cbbec517c"
limit_per_call = 500
# Max number of instances to be created
max_count = 40000

def main():  
    # Disable InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)   
    
    template_json = get_template(source_server, source_template_id, source_api_key)
    target_template_json = post_template(target_server, template_json, target_folder_id_template, target_api_key)
    target_template_id = target_template_json['@id']
    post_instances(source_server, target_server, source_template_id, target_template_id, target_folder_id_instances, max_count, limit_per_call, source_api_key, target_api_key)
    print("**** Done ****")

# Used to delete the template and instances created
# def main():  
#     # Disable InsecureRequestWarning
#     requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  
#     templ_id = "https://repo.metadatacenter.orgx/templates/cd292507-4a49-4326-8196-d262255c3507"
#     delete_instances(target_server, templ_id, max_count, limit_per_call, target_api_key)
#     print("**** Done ****")

def get_template(server, template_id, api_key):
    url = server + "templates/" + urllib.quote(template_id, safe='')
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    response = requests.request("GET", url, headers=headers)
    print("GET template response: " + str(response.status_code))
    return json.loads(response.text)

def get_instance(server, instance_id, api_key):
    url = server + "template-instances/" + urllib.quote(instance_id, safe='')
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    #print("GET instance response: " + str(response.status_code))
    return json.loads(response.text)   

def delete_instance(server, instance_id, api_key):
    url = server + "template-instances/" + urllib.quote(instance_id, safe='')
    print(url)
    headers = {
        'authorization': "apiKey " + api_key
    }
    response = requests.request("DELETE", url, headers=headers, verify=False)
    print("DELETE instance response: " + str(response.status_code))

def delete_template(server, template_id, api_key):
    url = server + "templates/" + urllib.quote(template_id, safe='')
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
    #print("POST template response: " + str(response.text))
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
        response_instances_summary = requests.request("GET", url_source_search, headers=headers, params=querystring, verify=False)
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

def post_instances(source_server, target_server, source_template_id, target_template_id, target_folder_id, max_count, limit_per_call, source_api_key, target_api_key):
    instances_summary = get_template_instances_summary(source_server, source_template_id, max_count, limit_per_call, source_api_key)
    url_target_instances = target_server + "template-instances"
    print('Retrieving full instances and posting them to the target system')
    total_count = len(instances_summary)
    count = 0
    for ins in instances_summary:
        instance = get_instance(source_server, ins['@id'], source_api_key)
        del instance['@id']
        instance['schema:isBasedOn'] = target_template_id
        querystring = {"folder_id": target_folder_id}
        headers = {
            'content-type': "application/json",
            'authorization': "apiKey " + target_api_key
        }
        response = requests.request("POST", url_target_instances, json=instance, headers=headers, params=querystring, verify=False)
        #print("POST instance response: " + str(response.status_code))
        print("Posted instance no. " + str(count) + " (" + str(float((100*count)/total_count)) + "%)")
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
