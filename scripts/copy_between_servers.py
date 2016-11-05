#!/usr/bin/python

# October-31-2016
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
source_api_key = "Your Api key here"
target_api_key = "Your Api key here"
target_folder_id_template = "https://repo.metadatacenter.orgx/folders/cf4d9eaf-aa9b-4693-812a-b8037653496b"
target_folder_id_instances = "https://repo.metadatacenter.orgx/folders/82f2fec1-3da9-43cd-98b4-fa13e8e4fea2"
template_id = "https://repo.staging.metadatacenter.net/templates/b62ae97c-6cdb-4431-9b00-938e6d19c9f3"
limit = 1000

def main():    
    template_json = get_template(source_server, template_id, source_api_key)
    new_template_json = post_template(target_server, template_json, target_folder_id_template, target_api_key)
    instances_json = get_template_instances(source_server, template_id, limit, source_api_key)
    post_instances(target_server, instances_json, new_template_json['@id'], target_folder_id_instances, target_api_key)
    print("**** Finished ****")

# Used to delete instances
# def main():    
#     templ_id = "https://repo.metadatacenter.orgx/templates/f1146f74-cab4-4dc4-9def-93c002b69c93"
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
    querystring = {"folderId": folder_id}
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    response = requests.request("POST", url, json=template, headers=headers, params=querystring, verify=False)
    print("POST template response: " + str(response.status_code))
    return json.loads(response.text)

def get_template_instances(server, template_id, limit, api_key):
    url = server + "search-deep"
    querystring = {"template_id": template_id,"limit":limit}
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

def post_instances(server, instances, new_template_id, folder_id, api_key):
    count = 1
    for instance in instances:
        del instance['@id']
        instance['schema:isBasedOn'] = new_template_id
        url = server + "template-instances"
        querystring = {"folderId": folder_id}
        headers = {
            'content-type': "application/json",
            'authorization': "apiKey " + api_key
        }
        response = requests.request("POST", url, json=instance, headers=headers, params=querystring, verify=False)
        print("POST instance response: " + str(response.status_code))
        print("Posted instance no. " + str(count))
        count = count + 1

def delete_instances(server, template_id, limit, api_key):
    instances_json = get_template_instances(server, template_id, limit, api_key)
    for instance in instances_json:
        delete_instance(server, instance['@id'], api_key)

if __name__ == "__main__":
    main()
