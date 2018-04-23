#!/usr/bin/python3

# Utility to extract all the unique values used in CEDAR instances and save them to different files

import json
import os
import annotation_constants

INSTANCE_PATHS = annotation_constants.VALUES_EXTRACTION_INSTANCE_PATHS
NCBI_BIOSAMPLE_ATTRIBUTES = annotation_constants.NCBI_RELEVANT_ATTRIBUTES
EBI_BIOSAMPLE_ATTRIBUTES = annotation_constants.EBI_RELEVANT_ATTRIBUTES
OUTPUT_FILE_PATH = annotation_constants.VALUES_EXTRACTION_OUTPUT_FILE_PATH


def main():

    if not os.path.exists(os.path.dirname(OUTPUT_FILE_PATH)):
        os.makedirs(os.path.dirname(OUTPUT_FILE_PATH))

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

    for att in annotation_constants.RELEVANT_ATTRIBUTES_NAMES:
        unique_values.add(att)

    print('No. unique values extracted: ' + str(len(unique_values)))

    # Save values
    with open(OUTPUT_FILE_PATH, 'w') as output_file:
        for value in unique_values:
            try:
                output_file.write("%s\n" % value)
            except:
                print('Error saving value: ' + value)


if __name__ == "__main__": main()
