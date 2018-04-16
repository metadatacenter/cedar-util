#!/usr/bin/python3

# Utility to annotate CEDAR instances using the NCBO Annotator. It takes a CEDAR instances and returns them annotated

import json
import os
from enum import Enum
import term_normalizer
import sys
import annotation_constants

# INPUT
INPUT_BASE_PATH = annotation_constants.INSTANCES_ANNOTATION_INPUT_BASE_PATH
INPUT_FOLDERS = annotation_constants.INSTANCES_ANNOTATION_INPUT_FOLDERS

# OUTPUT
OUTPUT_BASE_PATH = annotation_constants.INSTANCES_ANNOTATION_OUTPUT_BASE_PATH
OUTPUT_SUFFIX = annotation_constants.INSTANCES_ANNOTATION_OUTPUT_SUFFIX
NON_ANNOTATED_VALUES_REPORT_FILE_NAME = annotation_constants.INSTANCES_ANNOTATION_NON_ANNOTATED_VALUES_FILE_NAME

# OTHER CONSTANTS
UNIQUE_VALUES_ANNOTATED_FILE_PATH = annotation_constants.INSTANCES_ANNOTATION_VALUES_ANNOTATED_FILE_PATH
# The following two reference instances are using to extract the @type (instance types)
EBI_EMPTY_INSTANCE_ANNOTATED_PATH = annotation_constants.INSTANCES_ANNOTATION_EBI_EMPTY_INSTANCE_ANNOTATED_PATH
NCBI_EMPTY_INSTANCE_ANNOTATED_PATH = annotation_constants.INSTANCES_ANNOTATION_NCBI_EMPTY_INSTANCE_ANNOTATED_PATH
USE_NORMALIZED_VALUES = annotation_constants.INSTANCES_ANNOTATION_USE_NORMALIZED_VALUES
NORMALIZED_VALUES_FILE_NAME = annotation_constants.INSTANCES_ANNOTATION_NORMALIZED_VALUES_FILE_NAME  # We assume that the file is stored in the current path
NCBI_BIOSAMPLE_ATTRIBUTES = annotation_constants.NCBI_RELEVANT_ATTRIBUTES
EBI_BIOSAMPLE_ATTRIBUTES = annotation_constants.EBI_RELEVANT_ATTRIBUTES

total_values_count = 0
non_annotated_values = {}  # This dictionary will store all values that could not be annotated, as well as their frequency
non_annotated_values_count = 0


class BIOSAMPLES_DB(Enum):
    NCBI = 1
    EBI = 2


def annotate_instance(instance_json, unique_values_annotated, normalized_values, db=BIOSAMPLES_DB.NCBI):
    global total_values_count
    global non_annotated_values
    global non_annotated_values_count

    if db == BIOSAMPLES_DB.NCBI:
        att_list = NCBI_BIOSAMPLE_ATTRIBUTES
        reference_instance_json = json.load(open(NCBI_EMPTY_INSTANCE_ANNOTATED_PATH))
    elif db == BIOSAMPLES_DB.EBI:
        att_list = EBI_BIOSAMPLE_ATTRIBUTES
        reference_instance_json = json.load(open(EBI_EMPTY_INSTANCE_ANNOTATED_PATH))

    for att in att_list:
        att_value = instance_json[att]['@value']

        reference_att = reference_instance_json[att]
        att_type = None
        if '@type' in reference_att:
            att_type = reference_att['@type']
        if att_value is not None and len(att_value) > 0:
            total_values_count = total_values_count + 1
            instance_json[att] = {}
            att_value_normalized = term_normalizer.normalize_value(att_value, normalized_values)
            # print('----')
            # print(att_value)
            # print(att_value_normalized)
            if att_value_normalized in unique_values_annotated:
                instance_json[att]['@id'] = unique_values_annotated[att_value_normalized]['pref_class_uri']
                instance_json[att]['rdfs:label'] = unique_values_annotated[att_value_normalized]['pref_class_label']
                if att_type is not None:
                    instance_json[att]['@type'] = att_type
            else:
                non_annotated_values_count = non_annotated_values_count + 1
                if att_value not in non_annotated_values:
                    non_annotated_values[att_value_normalized] = 1
                else:
                    non_annotated_values[att_value_normalized] = non_annotated_values[att_value_normalized] + 1

        else:  # If there is no @value, we have to generate an empty object because @id cannot be null
            instance_json[att] = {}

    # print(instance_json)
    return instance_json


def main():
    annotations = json.load(open(UNIQUE_VALUES_ANNOTATED_FILE_PATH))

    normalized_values = {}
    if USE_NORMALIZED_VALUES:
        # Load file with normalized values
        normalized_values = json.loads(open(os.path.join(sys.path[0], NORMALIZED_VALUES_FILE_NAME)).read())

    # print(str(len(annotations)))
    # print(annotations['female'])
    count = 0

    for input_instances_path in INPUT_FOLDERS:
        output_path = OUTPUT_BASE_PATH + input_instances_path.replace(INPUT_BASE_PATH, '')
        print('Processing instances folder: ' + input_instances_path)
        for root, dirs, files in os.walk(input_instances_path):
            for file in files:
                if '.json' in file:  # basic check that we are processing the right file
                    instance_json = json.load(open(root + '/' + file, "r"))

                    if file.startswith('ncbi_'):
                        samples_db = BIOSAMPLES_DB.NCBI
                    elif file.startswith('ebi_'):
                        samples_db = BIOSAMPLES_DB.EBI
                    else:
                        raise Exception('Invalid file name')

                    annotated_instance = annotate_instance(instance_json, annotations, normalized_values, samples_db)

                    full_output_path = output_path + root.replace(input_instances_path, '')

                    if not os.path.exists(full_output_path):
                        os.makedirs(full_output_path)

                    output_file_path = full_output_path + '/' + os.path.splitext(file)[0] + OUTPUT_SUFFIX + '.json'

                    with open(output_file_path, 'w') as outfile:
                        json.dump(annotated_instance, outfile)

                    count = count + 1
                    if count % 100 == 0:
                        print("No. annotated instances: " + str(count))

        print()
        print('No. total values: ' + str(total_values_count))
        print('No. non annotated values: ' + str(non_annotated_values_count) + ' (' + "{0:.0f}%".format(
            non_annotated_values_count / total_values_count * 100) + ')')
        # Sort non annotated values by count
        sorted_non_annotated_values = sorted(((non_annotated_values[value], value) for value in non_annotated_values),
                                             reverse=True)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        non_annotated_values_file_path = output_path + '/' + NON_ANNOTATED_VALUES_REPORT_FILE_NAME
        with open(non_annotated_values_file_path, 'w') as outfile:
            json.dump(sorted_non_annotated_values, outfile, indent=4, separators=(',', ': '))


if __name__ == "__main__": main()
