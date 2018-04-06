#!/usr/bin/python3

# Utility to annotate CEDAR instances using the NCBO Annotator. It takes a CEDAR instances and returns them annotated

import json
import os
from enum import Enum
import term_normalizer
import sys

# Input
BASE_PATH = '/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_26_1-training_124200_ebi-testing-12800_ebi'
INSTANCES_FOLDER = 'training_samples_bla'
INSTANCES_BASE_PATH = BASE_PATH + '/' + INSTANCES_FOLDER
UNIQUE_VALUES_ANNOTATED_FILE_PATH = '/Users/marcosmr/tmp/ARM_resources/annotation_results/unique_values_annotated_bla.txt'

# Output (annotated instances)
OUTPUT_BASE_PATH = INSTANCES_BASE_PATH + '_annotated'
NON_ANNOTATED_VALUES_FILE_PATH = BASE_PATH + '/' + INSTANCES_FOLDER + '_non_annotated_values_report.txt'

NCBI_BIOSAMPLE_ATTRIBUTES = ['sex', 'tissue', 'cell_line', 'cell_type', 'disease', 'ethnicity', 'treatment']
EBI_BIOSAMPLE_ATTRIBUTES = ['sex', 'organismPart', 'cellLine', 'cellType', 'diseaseState', 'ethnicity']

NORMALIZED_VALUES_FILE_NAME = 'normalized_values.json'  # We assume that the file is stored in the current path

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
    elif db == BIOSAMPLES_DB.EBI:
        att_list = EBI_BIOSAMPLE_ATTRIBUTES

    for att in att_list:
        att_value = instance_json[att]['@value']
        if att_value is not None and len(att_value) > 0:
            total_values_count = total_values_count + 1
            instance_json[att] = {}
            att_value = term_normalizer.normalize_value(att_value, normalized_values)
            if att_value in unique_values_annotated:
                instance_json[att]['@id'] = unique_values_annotated[att_value]['pref_class_uri']
                instance_json[att]['rdfs:label'] = unique_values_annotated[att_value]['pref_class_label']
            else:
                non_annotated_values_count = non_annotated_values_count + 1
                if att_value not in non_annotated_values:
                    non_annotated_values[att_value] = 1
                else:
                    non_annotated_values[att_value] = non_annotated_values[att_value] + 1

        else:
            pass

    print(instance_json)
    return instance_json


def main():
    annotations = json.load(open(UNIQUE_VALUES_ANNOTATED_FILE_PATH))

    # Load file with normalized values
    normalized_values = json.loads(open(os.path.join(sys.path[0], NORMALIZED_VALUES_FILE_NAME)).read())

    # print(str(len(annotations)))
    # print(annotations['male'])
    count = 0
    for root, dirs, files in os.walk(INSTANCES_BASE_PATH):
        for file in files:
            if '.json' in file:  # basic check that we are processing the right file
                instance_json = json.load(open(root + '/' + file, "r"))

                if file.startswith('ncbi_'):
                    samples_db = BIOSAMPLES_DB.NCBI
                elif file.startswith('ebi_'):
                    samples_db = BIOSAMPLES_DB.EBI

                annotated_instance = annotate_instance(instance_json, annotations, normalized_values, samples_db)

                output_path = OUTPUT_BASE_PATH + root.replace(INSTANCES_BASE_PATH, '')

                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                output_file_path = output_path + '/' + os.path.splitext(file)[0] + '_annotated.json'

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

    with open(NON_ANNOTATED_VALUES_FILE_PATH, 'w') as outfile:
        json.dump(sorted_non_annotated_values, outfile, indent=4, separators=(',', ': '))


if __name__ == "__main__": main()
