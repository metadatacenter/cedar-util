#!/usr/bin/python3

# Utility to extract all the unique values used in CEDAR instances and saves them to different files (one file per instance field)...

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from random import shuffle
import bioportal_util
import os

INSTANCES_BASE_PATH_1 = '/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_25_1-training_124200_ncbi-testing-12800_ncbi/training_samples'
INSTANCES_BASE_PATH_2 = '/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_27_2-training_124200_ncbi-testing-13800_ncbi_NOSTRICT/testing_samples'
INSTANCES_BASE_PATH_3 = '/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_26_1-training_124200_ebi-testing-12800_ebi/training_samples'
INSTANCES_BASE_PATH_4 = '/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_27_5-training_124200_ebi-testing-13800_ebi_NOSTRICT_BASELINE/testing_samples'
INSTANCE_PATHS = [INSTANCES_BASE_PATH_1, INSTANCES_BASE_PATH_2, INSTANCES_BASE_PATH_3, INSTANCES_BASE_PATH_4]

NCBI_BIOSAMPLE_ATTRIBUTES = ['sex', 'tissue', 'cell_line', 'cell_type', 'disease', 'ethnicity', 'treatment']
EBI_BIOSAMPLE_ATTRIBUTES = ['sex', 'organismPart', 'cellLine', 'cellType', 'diseaseState', 'ethnicity']

OUTPUT_FILE_PATH = '/Users/marcosmr/tmp/ARM_resources/annotation_results/unique_values_lowercase.txt'


def main():
    count = 0
    unique_values = set()
    for path in INSTANCE_PATHS:
        for root, dirs, files in os.walk(path):
            for file in files:
                if '.json' in file:  # check that we are processing the right file
                    sample_json = json.load(open(root + '/' + file, "r"))  # Read file
                    if file.startswith('ncbi_'):
                        for att in NCBI_BIOSAMPLE_ATTRIBUTES:
                            value = sample_json[att]['@value']
                            if value is not None:
                                # print(value.lower())
                                unique_values.add(value.lower())

                    if file.startswith('ebi_'):
                        for att in EBI_BIOSAMPLE_ATTRIBUTES:
                            value = sample_json[att]['@value']
                            if value is not None:
                                # print(value.lower())
                                unique_values.add(value.lower())

                    count = count + 1
                    if count % 500 == 0:
                        print('No. files processed: ' + str(count))

    for att in NCBI_BIOSAMPLE_ATTRIBUTES:
        unique_values.add(att)
    for att in EBI_BIOSAMPLE_ATTRIBUTES:
        unique_values.add(att)

    # Save values
    with open(OUTPUT_FILE_PATH, 'w') as output_file:
        for value in unique_values:
            try:
                output_file.write("%s\n" % value)
            except:
                print('Error saving value: ' + value)


if __name__ == "__main__": main()
