#!/usr/bin/python3
import argparse
import os
from fnmatch import fnmatch
import json
import time

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
    parser.add_argument("--source-labels-path",
                        dest='source_labels_file_path',
                        required=False,
                        nargs=1,
                        metavar=("SOURCE_LABELS_FILE_PATH"),
                        help="file to read the normalized labels")
    parser.add_argument("--dest-labels-path",
                        dest='dest_labels_file_path',
                        required=True,
                        nargs=1,
                        metavar=("DEST_LABELS_FILE_PATH"),
                        help="file to save the normalized labels, so that they can be reused in the future without the need for making new BioPortal calls")
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
    dest_labels_file_path = args.dest_labels_file_path[0]

    labels_dict = {}  # labels cache
    if args.source_labels_file_path is not None:
        source_labels_file_path = args.source_labels_file_path[0]
        with open(source_labels_file_path) as f:
            labels_dict = json.load(f)

    relabel_instances(source_path, dest_path, fields_to_relabel, limit, bp_api_key, labels_dict, dest_labels_file_path)


def relabel_instances(source_path, dest_path, fields_to_relabel, limit, bp_api_key, labels_dict, dest_labels_file_path):
    """
    Relabels the values of all instances in a folder
    :param source_path:
    :param dest_path:
    :param fields_to_relabel:
    :param limit:
    :param bp_api_key:
    :param labels_dict:
    :return:
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
            relabeled_instance_json = relabel_values(instance_json, fields_to_relabel, bp_api_key, labels_dict)

            # Save transformed instance
            if not os.path.exists(os.path.dirname(relabeled_instance_path)):
                os.makedirs(os.path.dirname(relabeled_instance_path))

            with open(relabeled_instance_path, 'w') as output_file:
                json.dump(relabeled_instance_json, output_file, indent=4)
                print("Saved instance no. " + str(count) + " (" + str(float((100 * count) / total_count)) + "%) to "
                      + relabeled_instance_path)
            count += 1
            if count > limit:
                break;
        except ValueError:
            print('Decoding JSON has failed for this instance')

        # Save labels
        if dest_labels_file_path is not None:
            with open(dest_labels_file_path, 'w') as fp:
                json.dump(labels_dict, fp)


def relabel_values(instance_json, fields_to_relabel, bp_api_key, labels_dict):
    """

    :param instance_json:
    :param fields_to_relabel:
    :param bp_api_key:
    :param labels_dict:
    :return:
    """
    label_field = 'rdfs:label'

    for field in fields_to_relabel:
        if field in instance_json and label_field in instance_json[field]:
            current_label = instance_json[field][label_field]

            if current_label in labels_dict:
                print('hit cache!')
                new_label = labels_dict[current_label]
            else:
                new_label = get_bioportal_label(current_label, bp_api_key)

            normalized_new_label = normalize(new_label)

            if normalized_new_label is not None:
                labels_dict[current_label] = normalized_new_label
                instance_json[field][label_field] = normalized_new_label
            else:
                instance_json[field] = {}

            print(current_label + ' -> ' + str(normalized_new_label))

    return instance_json


def normalize(label):
    """

    :param label:
    :return:
    """
    if label is not None:
        # Capitalize first letter
        normalized_label = label[:1].upper() + label[1:]
    else:
        normalized_label = None

    return normalized_label


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
    response = None
    while count == 0 or response is None or response.status_code != 200:
        count = count + 1
        try:
            response = requests.post(url, json=payload, headers=headers, verify=False, timeout=10000)
            print('Payload: ' + str(payload))
            if response.status_code != 200:
                print('Problem when calling BioPortal search endpoint: ' + str(response.status_code) + '. Trying again...')
        except Exception as e:
            print(e)
            print('Problem when calling BioPortal search endpoint. Trying again...')

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
