#!/usr/bin/python3
import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib.parse
import json


# Utility to delete all instances of a given CEDAR template template
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server",
                        dest='server',
                        required=True,
                        nargs=1,
                        metavar=("SERVER_ADDRESS"),
                        help="the address of the CEDAR server. Example: https://resource.metadatacenter.orgx/")
    parser.add_argument("--api-key",
                        dest='api_key',
                        required=True,
                        nargs=1,
                        metavar=("API_KEY"),
                        help="CEDAR API key")
    parser.add_argument("--template-id",
                        dest='template_id',
                        required=True,
                        nargs=1,
                        metavar=("TEMPLATE_ID"),
                        help="template identifier. Example: https://repo.metadatacenter.orgx/templates/59cb865c-36d5-4c57-a06f-de074b5def71")

    args = parser.parse_args()
    server = args.server[0]
    api_key = args.api_key[0]
    template_id = args.template_id[0]
    max_count = 100000
    limit_per_call = 500
    delete_instances_from_template(server, template_id, max_count, limit_per_call, api_key)

# Returns summaries of the instances of the given template
def get_template_instances_summaries(server, template_id, max_count, limit_per_call, api_key):
    # print('*** Retrieving instance summaries of template: ' + template_id + ' ***')
    # Disable InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    instances_summary = []
    url = server + "search"
    offset = 0
    if max_count <= limit_per_call:
        limit_param = max_count
    else:
        limit_param = limit_per_call
    finished = False
    while not finished:
        querystring = {"is_based_on": template_id, "limit": limit_param, "offset": offset}
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
    return instances_summary  # Returns the ids of the instances of the given template


def get_template_instances_ids(server, template_id, max_count, limit_per_call, api_key):
    # Retrieve instances summaries
    summaries = get_template_instances_summaries(server, template_id, max_count, limit_per_call, api_key)
    ids = []
    for summary in summaries:
        ids.append(summary['@id'])
    return ids

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
    count = 1
    for instance_id in instance_ids:
        print('Deleting instance # ' + str(count))
        delete_instance(server, instance_id, api_key)
        count = count + 1


if __name__ == "__main__":
    main()
