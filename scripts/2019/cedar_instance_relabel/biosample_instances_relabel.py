#!/usr/bin/python3
import argparse
import os
from fnmatch import fnmatch
import json
import time

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

LABELS_DICT = {} # labels cache

# Utility to relabel ontology-based values in  CEDAR instances using the preferred label that corresponds to the ontology term
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-path",
                        dest='source_path',
                        required=True,
                        nargs=1,
                        metavar=("SOURCE_PATH"),
                        help="folder with the instances that need to be transformed")
    parser.add_argument("--dest-path",
                        dest='dest_path',
                        required=True,
                        nargs=1,
                        metavar=("DESTINATION_PATH"),
                        help = "folder where the transformed instances will be stored")
    parser.add_argument("--bp-api-key",
                        dest='bioportal_api_key',
                        required=True,
                        nargs=1,
                        metavar=("BIOPORTAL_API_KEY"),
                        help="BioPortal API Key")

    fields_to_relabel = ['sex', 'tissue', 'cell_line', 'cell_type', 'disease', 'ethnicity']
    limit = 200000 # Max number of instances to be processed

    args = parser.parse_args()
    source_path = args.source_path[0]
    dest_path = args.dest_path[0]
    bp_api_key = args.bioportal_api_key[0]

    relabel_instance(source_path, dest_path, fields_to_relabel, limit, bp_api_key)


def relabel_instance(source_path, dest_path, fields_to_relabel, limit, bp_api_key):
    """
    Relabels the values of all instances in a folder
    :param source_path:
    :param dest_path:
    :param fields_to_relabel:
    :return: It does not return anything. The transformed instances are saved to the destination path.
    """
    pattern = "*.json"
    instance_paths = []
    for path, subdirs, files in os.walk(source_path):
        for file_name in files:
            if fnmatch(file_name, pattern):
                instance_paths.append(os.path.join(path, file_name))
    # Load each instance and transform it
    count = 1;
    total_count = len(instance_paths)

    for instance_path in instance_paths:
        try:
            instance_json = json.load(open(instance_path))

            relabeled_instance_path = os.path.join(dest_path, os.path.relpath(instance_path, source_path))
            relabeled_instance_json = relabel_value(instance_json, fields_to_relabel, bp_api_key)

            # Save transformed instance
            # if not os.path.exists(os.path.dirname(relabeled_instance_path)):
            #     os.makedirs(os.path.dirname(relabeled_instance_path))
            #
            # with open(relabeled_instance_path, 'w') as output_file:
            #     json.dump(relabeled_instance_json, output_file, indent=4)
            #     print("Saved instance no. " + str(count) + " (" + str(float((100 * count) / total_count)) + "%) to "
            #           + relabeled_instance_path)
            count += 1
            if count > limit:
                break;
        except ValueError:
            print('Decoding JSON has failed for this instance')


def relabel_value(instance_json, fields_to_relabel, bp_api_key):
    """
    :param instance_json:
    :param fields_to_relabel:
    :return:
    """
    label_field = 'rdfs:label'

    for field in fields_to_relabel:
        if field in instance_json and label_field in instance_json[field]:
            current_label = instance_json[field][label_field]

            if current_label in LABELS_DICT:
                print('hit cache!')
                new_label = LABELS_DICT[current_label]
            else:
                new_label = get_bioportal_label(current_label, bp_api_key)
                LABELS_DICT[current_label] = new_label

            print(current_label + ' -> ' + new_label)
            if new_label is not None:
                instance_json[field][label_field] = new_label
            else:
                instance_json[field] = {}

    return instance_json


def get_bioportal_label(label, bp_api_key):
    """
    Gets the BP label with the right case
    :param label:
    :param bp_api_key:
    :return:
    """
    url = "https://data.bioontology.org/search"
    headers = {
        'content-type': "application/json",
        'authorization': "apikey token=" + bp_api_key
    }
    payload = {'q': label, 'require_exact_match': True}
    wait_amount = 0.1
    count = 0
    while count == 0 or response.status_code != 200:
        response = requests.post(url, json=payload, headers=headers, verify=False, timeout=10000)
        count = count + 1
        if response.status_code != 200:
            print('Url: ' + response.url)
            print('Problem when calling BioPortal search endpoint: ' + str(response.status_code) + '. Trying again...')

        time.sleep(wait_amount * count * 5)

    # print(payload)
    # print(response.url)
    # print(response.status_code)
    # print(response.text)
    results = json.loads(response.text)
    if len(results['collection']) > 0:
        for result in results['collection']:
            if result['prefLabel'].upper() == label:
                return result['prefLabel']


if __name__ == "__main__":
    main()
