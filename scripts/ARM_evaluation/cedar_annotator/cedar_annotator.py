#!/usr/bin/python3

# Utility to annotate CEDAR instances using the NCBO Annotator

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from random import shuffle
import cedar_util
import os

BASE_PATH = '/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_20_1-training_130K_ncbi-testing-5000_ebi/training_samples'
OUTPUT_BASE_PATH = '/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_20_1-training_130K_ncbi-testing-5000_ebi'
OUTPUT_FILE_NAME = 'sample_ids.txt'


def main():
    count = 0
    sample_ids = set()
    for root, dirs, files in os.walk(BASE_PATH):
        for file in files:
            if '.json' in file:  # check that we are processing the right file
                file_path = root + '/' + file
                sample_json = json.load(open(file_path, "r"))
                sample_id = sample_json['biosample_accession']['@value']
                sample_ids.add(sample_id)
                count = count + 1
                if count % 1000 == 0:
                    print('No. ids extracted: ' + str(count))

    # Save ids
    with open(OUTPUT_BASE_PATH + '/' + OUTPUT_FILE_NAME, 'w') as output_file:
        for sample_id in sample_ids:
            output_file.write("%s\n" % sample_id)


if __name__ == "__main__": main()
