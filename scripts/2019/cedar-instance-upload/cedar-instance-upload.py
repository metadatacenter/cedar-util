#!/usr/bin/python3

# Utility to upload CEDAR instances to a CEDAR server

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from fnmatch import fnmatch
import os
import json
import argparse
import sys

# Disable InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--server",
                        dest='server',
                        required=True,
                        nargs=1,
                        metavar=("SERVER_ADDRESS"),
                        help="the address of the CEDAR server. Example: https://resource.staging.metadatacenter.org/")
    parser.add_argument("--api-key",
                        dest='api_key',
                        required=True,
                        nargs=1,
                        metavar=("API_KEY"),
                        help="CEDAR API key")
    parser.add_argument("--source-path",
                        dest='source_path',
                        required=True,
                        nargs=1,
                        metavar=("SOURCE_PATH"),
                        help="path of the local folder that contains the instances to be uploaded")
    parser.add_argument("--cedar-folder-id",
                        dest='cedar_folder_id',
                        required=True,
                        nargs=1,
                        metavar=("CEDAR_FOLDER_ID"),
                        help="Identifier of the CEDAR folder where the instances will be stored")
    parser.add_argument("--cedar-template-id",
                        dest='cedar_template_id',
                        required=False,
                        nargs=1,
                        metavar=("CEDAR_TEMPLATE_ID"),
                        help="CEDAR template identifier. If provided, it will be used as the value of schema:isBasedOn for all the instances uploaded")
    parser.add_argument("--uploaded-file-path",
                        dest='uploaded_file_path',
                        required=False,
                        nargs=1,
                        metavar=("UPLOADED_FILE_PATH"),
                        help="File that will store the names of the uploaded instances. Optionally used to stop the upload and continue later without starting from the beginning")

    args = parser.parse_args()
    server = args.server[0]
    api_key = args.api_key[0]
    root_folder = args.source_path[0]
    target_cedar_folder_id = args.cedar_folder_id[0]

    if args.cedar_template_id is not None:
        template_id = args.cedar_template_id[0]
    else:
        template_id = None

    if args.uploaded_file_path is not None:
        uploaded_file_path = args.uploaded_file_path[0]
    else:
        uploaded_file_path = None

    upload_instances(server, root_folder, template_id, target_cedar_folder_id, api_key, uploaded_file_path)


def upload_instances(server, root_folder, template_id, target_cedar_folder_id, api_key, uploaded_file_path):
    """
    Uploads to the server all CEDAR instances in a folder and its subfolders
    :param server:
    :param root_folder:
    :param template_id:
    :param target_cedar_folder_id:
    :param api_key:
    :param uploaded_file_path:
    :return:
    """
    pattern = "*.json"
    instance_paths = []
    for path, subdirs, files in os.walk(root_folder):
        for name in files:
            if fnmatch(name, pattern):
                instance_paths.append(os.path.join(path, name))
    total_count = len(instance_paths)
    print('Number of instances upload: ' + str(total_count))

    # Array that keeps track of the uploaded instances
    if uploaded_file_path is not None:
        with open(uploaded_file_path, 'r') as f:
            uploaded = [x.strip() for x in f.readlines()]
    else:
        uploaded = []

    # Load each instance and upload it
    count = 1;
    with open(uploaded_file_path, 'a') as uploaded_instances_file:
        for instance_path in instance_paths:
            count += 1
            if instance_path not in uploaded:
                with open(instance_path) as data_file:
                    try:
                        instance_json = json.load(data_file)
                        response = post_instance(instance_json, template_id, server, target_cedar_folder_id, api_key)
                        if response.status_code != 201:
                            sys.exit(1)
                        print("Uploaded instance no. " + str(count) + " (" + str(float((100 * count) / total_count)) + "%)")
                        uploaded.append(instance_path)
                        uploaded_instances_file.write(instance_path + '\n')

                    except ValueError:
                        print('Decoding JSON has failed for this instance')
            else:
                print('Instance no. ' + str(count) + ' has been previously uploaded. It has been ignored')


def post_instance(instance, template_id, server, folder_id, api_key):
    url_instances = server + "template-instances"
    if '@id' in instance:
        del instance['@id']

    if template_id is not None:
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
    return response


if __name__ == "__main__":
    main()