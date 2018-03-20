#!/usr/bin/python3

# evaluation_main.py: Utility to perform the evaluation of the ARM-based metadata recommender

import time
import os
import json
import argparse
import numpy as np
import pandas as pd
from enum import Enum
# CEDAR dependencies
import arm_evaluation_util
import cedar_util


class BIOSAMPLES_DB(Enum):
    NCBI = 1
    EBI = 2


# Execution Settings
MAX_NUMBER_INSTANCES = 2000  # Max number of instances that will be part of the test set

TRAINING_DB = BIOSAMPLES_DB.NCBI
TESTING_DB = BIOSAMPLES_DB.EBI

READ_TEST_INSTANCES_FROM_CEDAR = False  # If false, the instances are read from a local folder
VR_SERVER = 'https://valuerecommender.metadatacenter.orgx/'
NCBI_TEMPLATE_ID = 'https://repo.metadatacenter.orgx/templates/eef6f399-aa4e-4982-ab04-ad8e9635aa91'
EBI_TEMPLATE_ID = 'https://repo.metadatacenter.orgx/templates/6b6c76e6-1d9b-4096-9702-133e25ecd140'
EXPORT_RESULTS_PATH = '/Users/marcosmr/tmp/ARM_resources/evaluation_results'

NCBI_TEST_INSTANCES_LOCAL_BASE_FOLDER = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/cedar_instances/homo_sapiens-min_3_attribs_valid/testing'
EBI_TEST_INSTANCES_LOCAL_BASE_FOLDER = '/Users/marcosmr/tmp/ARM_resources/ebi_biosamples/cedar_instances/homo_sapiens-min_3_attribs_valid/testing'

# Relevant fields, with their paths and json path expressions
NCBI_FIELD_DETAILS = {'sex': {'path': 'sex', 'json_path': '$.sex'},
                      'tissue': {'path': 'tissue', 'json_path': '$.tissue'},
                      'cell_line': {'path': 'cell_line', 'json_path': '$.cell_line'},
                      'cell_type': {'path': 'cell_type', 'json_path': '$.cell_type'},
                      'disease': {'path': 'disease', 'json_path': '$.disease'},
                      'ethnicity': {'path': 'ethnicity', 'json_path': '$.ethnicity'},
                      'treatment': {'path': 'treatment', 'json_path': '$.treatment'}}

# Other constants
EBI_BIOSAMPLE_BASIC_FIELDS = ['accession', 'name', 'releaseDate', 'updateDate', 'organization', 'contact']
EBI_BIOSAMPLE_ATTRIBUTES = ['organism', 'age', 'sex', 'organismPart', 'cellLine', 'cellType', 'diseaseState',
                            'ethnicity']

EBI_FIELD_DETAILS = {'sex': {'path': 'sex', 'json_path': '$.sex'},
                     'organismPart': {'path': 'organismPart', 'json_path': '$.organismPart'},
                     'cellLine': {'path': 'cellLine', 'json_path': '$.cellLine'},
                     'cellType': {'path': 'cellType', 'json_path': '$.cellType'},
                     'diseaseState': {'path': 'diseaseState', 'json_path': '$.diseaseState'},
                     'ethnicity': {'path': 'ethnicity', 'json_path': '$.ethnicity'}}

EBI_TO_NCBI_MAPPINGS = {
    'sex': 'sex', 'organismPart': 'tissue', 'cellLine': 'cell_line', 'cellType': 'cell_type', 'diseaseState': 'disease',
    'ethnicity': 'ethnicity'}

NCBI_TO_EBI_MAPPINGS = {}  # TODO


# TODO
def get_mapped_field_path(field_name, training_db=TRAINING_DB, testing_db=TESTING_DB,
                          ebi_to_ncbi_mappings=EBI_TO_NCBI_MAPPINGS,
                          ncbi_to_ebi_mappings=NCBI_TO_EBI_MAPPINGS,
                          ncbi_field_details=NCBI_FIELD_DETAILS,
                          ebi_field_detail=EBI_FIELD_DETAILS):
    field_path = None
    if training_db == BIOSAMPLES_DB.NCBI:
        if testing_db == BIOSAMPLES_DB.NCBI:
            return ncbi_field_details[field_name]['path']
        elif testing_db == BIOSAMPLES_DB.EBI:
            mapped_field_name = EBI_TO_NCBI_MAPPINGS[field_name]
            return ncbi_field_details[mapped_field_name]['path']

    elif training_db == BIOSAMPLES_DB.EBI:
        if testing_db == BIOSAMPLES_DB.EBI:
            pass
        elif testing_db == BIOSAMPLES_DB.EBI:
            pass


def get_mapped_populated_fields(field_details, field_values, target_field):
    """
    Returns the populated fields body, given the target field
    :param field_details: 
    :param field_values: 
    :param target_field: 
    :return: 
    """
    populated_fields = []
    for f in field_values:
        if f != target_field:
            if field_values[f] is not None:
                mapped_field_path = get_mapped_field_path(field_details[f]['path'])
                populated_fields.append({'path': mapped_field_path, 'value': field_values[f]})
    return populated_fields


def main():
    # Read api key from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("apiKey", help="Your CEDAR apiKey")
    args = parser.parse_args()
    api_key = args.apiKey

    results_database = []
    results_instance_ids = []
    results_populated_fields = []
    results_populated_fields_size = []
    results_field_names = []
    results_expected_values = []
    results_top1_values_vr = []
    results_correct_recommendations_vr = []
    results_top3_values_vr = []
    results_reciprocal_rank_vr = []
    results_reciprocal_rank_vr_no_na = []
    results_exec_times_vr = []
    start_time = time.time()

    instances_count = 1
    if TESTING_DB == BIOSAMPLES_DB.NCBI:
        field_details = NCBI_FIELD_DETAILS
        test_instances_base_folder = NCBI_TEST_INSTANCES_LOCAL_BASE_FOLDER
    elif TESTING_DB == BIOSAMPLES_DB.EBI:
        field_details = EBI_FIELD_DETAILS
        test_instances_base_folder = EBI_TEST_INSTANCES_LOCAL_BASE_FOLDER

    if TRAINING_DB == BIOSAMPLES_DB.NCBI and TESTING_DB == BIOSAMPLES_DB.NCBI:
        template_id = NCBI_TEMPLATE_ID
    elif TRAINING_DB == BIOSAMPLES_DB.EBI and TESTING_DB == BIOSAMPLES_DB.EBI:
        template_id = EBI_TEMPLATE_ID
    else:
        template_id = None

    if READ_TEST_INSTANCES_FROM_CEDAR:
        pass  # TODO
    else:  # Read from local folder
        print('Reading test instances from: ' + test_instances_base_folder)
        for root, dirs, files in os.walk(test_instances_base_folder):
            for file in files:
                if 'biosample_instance' in file and instances_count <= MAX_NUMBER_INSTANCES:  # check that we are processing the right file
                    file_path = root + '/' + file
                    # Read instance
                    instance_json = json.load(open(file_path))
                    # Read instance field values
                    field_values = arm_evaluation_util.get_instance_fields_values(instance_json, field_details)
                    for field_name in field_values:
                        if field_values[field_name] is not None:  # if the field is not empty
                            # Extract populated fields considering that fv is the target field
                            populated_fields = get_mapped_populated_fields(field_details,
                                                                           field_values,
                                                                           field_name)

                            field_path = get_mapped_field_path(field_name)

                            # Run the value recommender for the given field and populated fields
                            start_time_vr = time.time()
                            recommendation_vr = cedar_util.get_value_recommendation(VR_SERVER, template_id, field_path,
                                                                                    populated_fields,
                                                                                    api_key)
                            execution_time_vr = int(round((time.time() - start_time_vr) * 1000))

                            recommended_top1_value_vr = arm_evaluation_util.get_recommended_values(recommendation_vr, 1)
                            is_correct_vr = arm_evaluation_util.get_matching_score(field_values[field_name],
                                                                                   arm_evaluation_util.get_recommended_values_as_string(
                                                                                       recommended_top1_value_vr))

                            if is_correct_vr == 1:
                                print('got it right!')

                            recommended_top3_values_vr = arm_evaluation_util.get_recommended_values(recommendation_vr,
                                                                                                    3)
                            reciprocal_rank_vr = arm_evaluation_util.reciprocal_rank(field_values[field_name],
                                                                                     recommended_top3_values_vr)

                            # this is the reciprocal rank with 0s instead of NAs
                            reciprocal_rank_vr_no_na = arm_evaluation_util.reciprocal_rank(field_values[field_name],
                                                                                           recommended_top3_values_vr,
                                                                                           False)

                            # Store results in arrays
                            instance_id = instances_count  # There is no id for instances read from a local folder so we just store the count
                            results_instance_ids.append(instance_id)
                            results_database.append(TESTING_DB.name)
                            results_populated_fields.append(
                                arm_evaluation_util.populated_fields_to_string(populated_fields))
                            results_populated_fields_size.append(str(len(populated_fields)))
                            results_field_names.append(field_name)
                            results_expected_values.append(field_values[field_name])
                            results_top1_values_vr.append(
                                arm_evaluation_util.get_recommended_values_as_string(recommended_top1_value_vr))
                            results_correct_recommendations_vr.append(is_correct_vr)
                            results_top3_values_vr.append(
                                arm_evaluation_util.get_recommended_values_as_string(recommended_top3_values_vr))
                            results_reciprocal_rank_vr.append(reciprocal_rank_vr)
                            results_reciprocal_rank_vr_no_na.append(reciprocal_rank_vr_no_na)
                            results_exec_times_vr.append(execution_time_vr)

                    instances_count = instances_count + 1
                    print('No. instances processed: ' + str(instances_count))

        # Stack the 1-D arrays generated as columns into a 2-D array
        results = np.column_stack(
            (results_database, results_instance_ids, results_populated_fields, results_populated_fields_size,
             results_field_names, results_expected_values,
             results_top1_values_vr, results_correct_recommendations_vr,
             results_top3_values_vr, results_reciprocal_rank_vr, results_reciprocal_rank_vr_no_na,
             results_exec_times_vr))

        results_df = pd.DataFrame(results,
                                  columns=['database', 'instance_id', 'populated_fields', 'populated_fields_size',
                                           'target_field', 'expected_value', 'top1_value_vr', 'is_correct_vr',
                                           'top3_values_vr', 'RR_vr', 'RR_vr_no_NA', 'exec_time_vr'])

        print("\nExecution time:  %s seconds " % (time.time() - start_time))

        # Export results
        current_time = time.strftime("%Y-%m-%d_%H_%M_%S", time.gmtime())
        # results_path = EXPORT_RESULTS_PATH + '/' + current_time
        results_path = EXPORT_RESULTS_PATH
        if not os.path.exists(results_path):
            os.makedirs(results_path)

        # to CSV
        results_df.to_csv(
            results_path + '/' + 'results_train-' + TRAINING_DB.name + '_test-' + TESTING_DB.name +
            '_' + str(instances_count - 1) + 'instances_' + current_time + '.csv',
            index=False, header=True)

        # Analysis of results
        # results_analysis.analyze_results(results_df)


if __name__ == "__main__": main()
