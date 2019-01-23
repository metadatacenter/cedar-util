# CEDAR operations module

# Last updated: Aug-9-2017

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import urllib.parse
import os
from fnmatch import fnmatch


# Returns summaries of the instances of the given template
def get_template_instances_summaries(server, template_id, max_count, limit_per_call, api_key):
    # print('*** Retrieving instance summaries of template: ' + template_id + ' ***')
    # Disable InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    instances_summary = []
    url = server + "search-deep"
    offset = 0
    if max_count <= limit_per_call:
        limit_param = max_count
    else:
        limit_param = limit_per_call
    finished = False
    while not finished:
        querystring = {"q": "*", "derived_from_id": template_id, "limit": limit_param, "offset": offset}
        headers = {
            'content-type': "application/json",
            'authorization': "apiKey " + api_key
        }
        response_instances_summary = requests.request("GET", url, headers=headers, params=querystring, verify=False)
        # print("GET instances summary URL: " + str(response_instances_summary.url))
        # print("GET instances summary response: " + str(response_instances_summary.status_code))
        response_json = json.loads(response_instances_summary.text)
        instances_summary.extend(response_json["resources"])

        offset = offset + limit_param

        if not len(response_json["resources"]):
            finished = True

        if (offset + limit_param) > max_count:
            if offset < max_count:
                limit_param = max_count - offset
            else:
                finished = True

    # print('Total number of instance summaries retrieved: ' + str(len(instances_summary)))
    return instances_summary


# Returns the ids of the instances of the given template
def get_template_instances_ids(server, template_id, max_count, limit_per_call, api_key):
    # Retrieve instances summaries
    summaries = get_template_instances_summaries(server, template_id, max_count, limit_per_call, api_key)
    ids = []
    for summary in summaries:
        ids.append(summary['@id'])
    return ids


def get_template_instance_by_id(server, template_instance_id, api_key):
    url = server + "template-instances/" + urllib.parse.quote(template_instance_id, safe='')
    headers = {
         'content-type': "application/json",
         'authorization': "apiKey " + api_key
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    return json.loads(response.text)


def get_value_recommendation(server, template_id, target_field_path, populated_fields, api_key):
    url = server + "recommend"
    if populated_fields is not None:
        payload = {'templateId': template_id, 'targetField': {'path': target_field_path}, 'populatedFields': populated_fields}
    else:
        payload = {'templateId': template_id, 'targetField': {'path': target_field_path}}
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    recommendation_response = requests.post(url, json=payload, headers=headers, verify=False)
    # print(payload)
    # print(recommendation_response.url)
    # print(recommendation_response.text)
    return json.loads(recommendation_response.text)


def post_instance(instance, server, template_id, folder_id, api_key):
    url_instances = server + "template-instances"
    if '@id' in instance:
        del instance['@id']
    instance['schema:isBasedOn'] = template_id
    querystring = {"folder_id": folder_id}
    headers = {
        'content-type': "application/json",
        'authorization': "apiKey " + api_key
    }
    response = requests.request("POST", url_instances, json=instance, headers=headers, params=querystring, verify=False)
    print("POST instance response: " + str(response.status_code))
    # print("POST instance response: " + str(response.url))
    # print("POST instance response: " + str(response.text))


def delete_instance(server, instance_id, api_key):
    # Disable InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    url = server + "template-instances/" + urllib.parse.quote(instance_id, safe='')
    print(url)
    headers = {
        'authorization': "apiKey " + api_key
    }
    response = requests.request("DELETE", url, headers=headers, verify=False)
    print("DELETE instance response: " + str(response.status_code))


# Removes all instances from a particular template
def delete_instances_from_template(server, template_id, max_count, limit_per_call, api_key):
    instance_ids = get_template_instances_ids(server, template_id, max_count, limit_per_call, api_key)
    for instance_id in instance_ids:
        delete_instance(server, instance_id, api_key)


# Reads all instances in a folder and uploads them to the server
def load_instances_from_folder_and_upload(server, root_folder, template_id, target_cedar_folder_id, api_key):
    # Disable InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    pattern = "*.json"
    instance_paths = []
    for path, subdirs, files in os.walk(root_folder):
        for name in files:
            if fnmatch(name, pattern):
                instance_paths.append(os.path.join(path, name))
    print(len(instance_paths))
    # Load each instance and push it to the system
    count = 1;
    total_count = len(instance_paths)
    for instance_path in instance_paths:
        with open(instance_path) as data_file:
            try:
                instance_json = json.load(data_file)
                post_instance(instance_json, server, template_id, target_cedar_folder_id, api_key)
                print("Posted instance no. " + str(count) + " (" + str(float((100 * count) / total_count)) + "%)")
                count += 1
            except ValueError:
                print('Decoding JSON has failed for this instance')

# Reads all json files in a folder
def load_json_file_paths_from_folder(root_folder):
    files = []
    # Disable InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    pattern = "*.json"
    file_paths = []
    for path, subdirs, files in os.walk(root_folder):
        for name in files:
            if fnmatch(name, pattern):
                file_paths.append(os.path.join(path, name))
    return file_paths

# Loads a json file
def load_json_file(file_path):
    # Disable InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    with open(file_path) as data_file:
            try:
                file_json = json.load(data_file)
                return file_json
            except ValueError:
                print('Error decoding JSON')
