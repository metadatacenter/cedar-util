#!/usr/bin/python3

# Utility to merge two mapping files into one
#

import json
import annotation_constants


def merge_mappings(mappings1, mappings2):
    """
    Merges two mapping dictionaries
    :param mappings1: 
    :param mappings2
    """
    mappings = mappings1.copy()

    for key_uri in mappings2:
        if key_uri not in mappings:
            mappings[key_uri] = mappings2[key_uri]
        else:
            for uri in mappings2[key_uri]:
                if uri not in mappings[key_uri]:
                    mappings[key_uri].append(uri)
    return mappings


def main():
    mappings1 = json.load(open(annotation_constants.MAPPINGS_MERGING_MAPPINGS_PATH_1))
    mappings2 = json.load(open(annotation_constants.MAPPINGS_MERGING_MAPPINGS_PATH_2))
    mappings_fields = json.load(open(annotation_constants.MAPPINGS_MERGING_MAPPINGS_FIELDS))

    mappings_merged = merge_mappings(mappings1, mappings2)
    mappings_merged_final = merge_mappings(mappings_merged, mappings_fields)

    with open(annotation_constants.MAPPINGS_MERGING_OUTPUT_MAPPINGS_FILE_PATH, 'w') as outfile:
        json.dump(mappings_merged_final, outfile)

    print('The mappings files have been merged.')


if __name__ == "__main__": main()
