#!/usr/bin/python

# Created:      Oct-31-2016
# Last updated: Jan-31-2017
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
import os.path
import sys
import jsclean
import time
from datetime import datetime
import json
import urllib

source_server = "https://resource.staging.metadatacenter.net/"
target_server = "https://resource.metadatacenter.orgx/"
source_api_key = "Source API key here"
target_api_key = "Target API key here"
target_folder_id_template = "https://repo.metadatacenter.orgx/folders/3d855ac0-dae6-401e-bd0b-6a858d01d535"
target_folder_id_instances = "https://repo.metadatacenter.orgx/folders/6b7a6775-a621-4539-b8bd-f762077e7f1a"
source_template_id = "https://repo.staging.metadatacenter.net/templates/99de8dbb-5e26-4b31-928e-903cbbec517c"
limit = 100000

def main():    
    template_json = get_template(source_server, source_template_id, source_api_key)
    target_template_json = post_template(target_server, template_json, target_folder_id_template, target_api_key)
    target_template_id = target_template_json['@id']
    post_instances(source_server, target_server, source_template_id, target_template_id, target_folder_id_instances, limit, source_api_key, target_api_key)
    print("**** Finished ****")

# Used to delete instances
# def main():    
#     templ_id = "https://repo.metadatacenter.orgx/templates/aa9e244e-cb5f-462c-9687-6406e8b8edcf"
#     limit = 100
#     delete_instances(target_server, templ_id, limit, target_api_key)
#     print("**** Finished ****")

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
    print("GET instance response: " + str(response.status_code))
    return json.loads(response.text)   

def delete_instance(server, instance_id, api_key):
    url = server + "template-instances/" + urllib.quote(instance_id, safe='')
    print(url)
    headers = {
        'authorization': "apiKey " + api_key
    }
    response = requests.request("DELETE", url, headers=headers, verify=False)
    print("DELETE instance response: " + str(response.status_code))

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

def get_template_instances(server, template_id, limit, api_key):
    url = server + "search-deep"
    querystring = {"derived_from_id": template_id,"offset":limit}
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    response = requests.request("GET", url, headers=headers, params=querystring, verify=False)
    print("GET template instances response: " + str(response.status_code))
    response_json = json.loads(response.text)
    instances = []
    for resource in response_json['resources']:
        instance = get_instance(server, resource['@id'], api_key)
        instances.append(instance)
    return instances

def post_instances(source_server, target_server, source_template_id, target_template_id, target_folder_id, limit, source_api_key, target_api_key):
    # Retrieve basic info for instances
    url_source_search = source_server + "search-deep"
    querystring = {"derived_from_id": source_template_id,"offset":limit}
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + source_api_key
    }
    response_instances = requests.request("GET", url_source_search, headers=headers, params=querystring, verify=False)
    print("GET instances response: " + str(response_instances.status_code))
    response_json = json.loads(response_instances.text)
    total_count = len(response_json["resources"])
    print("Number of instances retrieved: " + str(total_count))
    url_target_instances = target_server + "template-instances"
    count = 1
    for resource in response_json['resources']:
        # Retrieve instance
        instance = get_instance(source_server, resource['@id'], source_api_key)
        # Post instance to the target server
        del instance['@id']
        instance['schema:isBasedOn'] = target_template_id
        querystring = {"folder_id": target_folder_id}
        headers = {
            'content-type': "application/json",
            'authorization': "apiKey " + target_api_key
        }
        response = requests.request("POST", url_target_instances, json=instance, headers=headers, params=querystring, verify=False)
        print("POST instance response: " + str(response.status_code))
        print("Posted instance no. " + str(count) + " (" + str(float((100*count)/total_count)) + "%)")
        count = count + 1

def delete_instances(server, template_id, limit, api_key):
    instances_json = get_template_instances(server, template_id, limit, api_key)
    for instance in instances_json:
        delete_instance(server, instance['@id'], api_key)

if __name__ == "__main__":
    main()
