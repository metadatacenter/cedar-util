#!/usr/bin/python3

# evaluation_main.py: Utility to perform the evaluation of the ARM-based metadata recommender

import time
import os
import json
import argparse
# CEDAR dependencies
import arm_evaluation_util
import cedar_util

# Constants
READ_TEST_INSTANCES_FROM_CEDAR = False  # If false, the instances are read from a local folder
TEST_INSTANCES_LOCAL_BASE_FOLDER = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/cedar_instances'
VR_SERVER = "https://valuerecommender.metadatacenter.orgx/"
TEMPLATE_ID = "https://repo.metadatacenter.orgx/templates/eef6f399-aa4e-4982-ab04-ad8e9635aa91"

# Relevant fields, with their paths and json path expressions
NCBI_FIELD_DETAILS = {'sex': {'path': 'sex', 'json_path': '$.sex'},
                      'tissue': {'path': 'tissue', 'json_path': '$.tissue'},
                      'cell_line': {'path': 'cell_line', 'json_path': '$.cell_line'},
                      'cell_type': {'path': 'cell_type', 'json_path': '$.cell_type'},
                      'disease': {'path': 'disease', 'json_path': '$.disease'},
                      'ethnicity': {'path': 'ethnicity', 'json_path': '$.ethnicity'},
                      'treatment': {'path': 'treatment', 'json_path': '$.treatment'}}


# EBI_FIELD_PATHS = {'sex': {'path': 'sex', 'json_path': '$.sex'},
#                     'tissue': {'path': 'tissue', 'json_path': '$.tissue'},
#                     'cell_line': {'path': 'cell_line', 'json_path': '$.cell_line'},
#                     'cell_type': {'path': 'cell_type', 'json_path': '$.cell_type'},
#                     'disease': {'path': 'disease', 'json_path': '$.disease'},
#                     'ethnicity': {'path': 'ethnicity', 'json_path': '$.ethnicity'},
#                     'treatment': {'path': 'treatment', 'json_path': '$.treatment'}}

def main():
    # Read api key from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("apiKey", help="Your CEDAR apiKey")
    args = parser.parse_args()
    api_key = args.apiKey

    start_time = time.time()
    if READ_TEST_INSTANCES_FROM_CEDAR:
        pass  # TODO
    else:  # Read from local folder
        for root, dirs, files in os.walk(TEST_INSTANCES_LOCAL_BASE_FOLDER):
            for file in files:
                if 'biosample_instance' in file:  # check that we are processing the right file
                    file_path = root + '/' + file
                    # Read instance
                    instance_json = json.load(open(file_path))
                    # Read instance field values
                    field_values = arm_evaluation_util.get_instance_fields_values(instance_json, NCBI_FIELD_DETAILS)

                    for field_name in field_values:
                        # Extract populated fields considering that fv is the target field
                        populated_fields = arm_evaluation_util.get_populated_fields(NCBI_FIELD_DETAILS, field_values,
                                                                                    field_name)

                        # Get recommendation from the value recommender
                        field_path = NCBI_FIELD_DETAILS[field_name]['path']
                        recommendation_vr = cedar_util.get_value_recommendation(VR_SERVER, TEMPLATE_ID, field_path,
                                                                                populated_fields,
                                                                                api_key)

                        recommended_top3_values_vr = arm_evaluation_util.get_recommended_values(recommendation_vr, 3)
                        reciprocal_rank_vr = arm_evaluation_util.reciprocal_rank(field_values[field_name],
                                                                                 recommended_top3_values_vr)

                        print(reciprocal_rank_vr)


if __name__ == "__main__": main()
