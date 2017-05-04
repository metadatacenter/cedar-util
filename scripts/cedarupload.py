#!/usr/bin/python

# July-20-2016
# cedarupload.py: Utility to create requests and execute them on CEDAR resources
#
# - Takes parameters needed for a CEDAR REST API POST request
# - Iterates through a directory to post all files to specified host name
# - Creates log file log.txt with request status, reason, headers, timing, and other information

import argparse
import requests
import os.path
import sys
import jsclean
import time
from datetime import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--apiKey", help="authorization for upload to CEDAR", required=True)
    parser.add_argument("-n", "--hostName", help="site host name")
    parser.add_argument("-d", "--directory", help="directory of files to upload", required=True)
    parser.add_argument("-f", "--folderId", help="URL of CEDAR folder files will be uploaded to", required=True)
    # parser.add_argument("-r", "--resource", help="name of CEDAR resource in directory", required=False)

    args = parser.parse_args()
    api_key = args.apiKey
    host_name = args.hostName
    directory = args.directory
    folder_id = args.folderId
    # resource = args.resource

    if not os.path.exists(directory):
        print("Input directory does not exist. Please try again.")
        sys.exit()

    url, parameter, headers = create_command(api_key, host_name, folder_id)
    cedar_post(url, parameter, headers, directory)


def cedar_post(url, parameter, headers, directory):
    log_file = os.path.join(directory, "log.txt")
    with open(log_file, 'a') as log:
        directory_files = jsclean.directory_walk(directory)
        log.write("\n**** Start upload ****\n")

        start = time.time()
        for cedar_file in directory_files:
            with open(cedar_file, 'rb') as f:
                json_data = f.read()
            r = requests.post(url, params=parameter, data=json_data, headers=headers)   # make request

            #  log information
            request_time = time.time() - start
            log.write("\n")
            cur_time = "Current time: " + str(datetime.now()) + "\n"
            log.write(cur_time)
            response = cedar_file + "\n\t" + str(r.status_code).encode('utf-8') + ": " + r.reason + "\n\t" + \
                str(request_time) + "\n\t" + str(r.url.encode('utf-8')) + "\n"
            log.write(response)
            resp_headers = "Headers:     " + str(r.request.headers).encode('utf-8') + "\n\n"
            log.write(resp_headers)
            try:
                resp_text = "Text:     " + str(r.text).encode('utf-8') + "\n\n\n"
            except UnicodeEncodeError:
                resp_text = "text failed to encode \n\n\n"
            log.write(resp_text)
            print(cur_time + response + resp_headers + resp_text)
        end = time.time()

        elapsed = end - start
        elapsed_message = "\nElapsed time: " + str(elapsed) + "\n"
        log.write(elapsed_message)
        log.write("\n**** Finish upload ****\n")
        print(elapsed_message)


def create_command(api_key, host_name, folder_id):
    parameter = {'folderId': folder_id}
    cedar_resource = pick_resource(resource='template-instances')  # re-include argument to enable resource choice
    url = "https://" + host_name + "/" + cedar_resource
    api_header = 'apiKey ' + api_key
    headers = {'Content-Type': 'application/json', 'Authorization': api_header}
    return url, parameter, headers


def pick_resource(resource):
    resource_list = ['template-elements', 'template-fields', 'template-instances', 'templates']
    if resource in resource_list:
        return resource


if __name__ == "__main__":
    main()
