#!/usr/bin/python3

# Utility to count the number of plain text values vs annotated values per field

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from random import shuffle
import cedar_util
import os

BASE_PATH = "/Users/marcosmr/tmp/ARM_resources/EVALUATION"

NCBI_TEXT = BASE_PATH + '/cedar_instances/ncbi_cedar_instances'
EBI_TEXT = BASE_PATH + '/cedar_instances/ebi_cedar_instances'

NCBI_ANNOTATED = BASE_PATH + '/cedar_instances_annotated/ncbi_cedar_instances'
EBI_ANNOTATED = BASE_PATH + '/cedar_instances_annotated/ebi_cedar_instances'


NCBI_RELEVANT_ATTS = ['sex', 'tissue', 'disease', 'cell_type', 'cell_line', 'ethnicity']
EBI_RELEVANT_ATTS = ['sex', 'organismPart', 'diseaseState', 'cellType', 'cellLine', 'ethnicity']


def count_values(file_path, relevant_atts, annotated):
    value_field = '@value'
    if annotated:
        value_field = '@id'
    count = 0
    unique_values = {}
    results = {"all": {}, "unique": {}}
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if '.json' in file:  # check that we are processing the right file
                file_path = root + '/' + file
                sample_json = json.load(open(file_path, "r"))
                for att in relevant_atts:
                    if att not in results['all']:
                        results['all'][att] = 0
                    if att not in results['unique']:
                        results['unique'][att] = 0
                    if att not in unique_values:
                        unique_values[att] = []
                    else:
                        if att in sample_json and value_field in sample_json[att] and sample_json[att][value_field] is not None \
                                and sample_json[att][value_field] != "":
                            # count all values
                            results['all'][att] = results['all'][att] + 1
                            # count unique values
                            v = sample_json[att][value_field]
                            if v not in unique_values[att]:
                                unique_values[att].append(v)
                                results['unique'][att] = len(unique_values[att])

                count = count + 1

                if count % 10000 == 0:
                #     print('No. samples checked: ' + str(count))
                    #print(results)
                    print(unique_values["sex"])
    print(results)


def main():
    #print("NCBI-TEXT")
    #count_values(NCBI_TEXT, NCBI_RELEVANT_ATTS, False)
    print("NCBI-ANNOTATED")
    count_values(NCBI_ANNOTATED, NCBI_RELEVANT_ATTS, True)
    # print("EBI-TEXT")
    # count_values(EBI_TEXT, EBI_RELEVANT_ATTS, False)
    # print("EBI-ANNOTATED")
    # count_values(EBI_ANNOTATED, EBI_RELEVANT_ATTS, True)


if __name__ == "__main__": main()
