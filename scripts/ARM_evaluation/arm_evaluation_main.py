#!/usr/bin/python3

# evaluation_main.py: Utility to perform the evaluation of the ARM-based metadata recommender

import time
import os
import json
import argparse
import numpy as np
import pandas as pd
import itertools
# CEDAR dependencies
import arm_evaluation_util
import arm_constants
from arm_constants import BIOSAMPLES_DB
import cedar_util

# Input # Don't forget to regenerate the most frequent values from the ARFF files if needed
TRAINING_DB = BIOSAMPLES_DB.EBI
TESTING_DB = BIOSAMPLES_DB.NCBI
VR_STRICT_MATCH = False
MAX_NUMBER_INSTANCES = 10  # Max number of instances that will be part of the test set
ANNOTATED_VALUES = True
EXTEND_URIS_WITH_MAPPINGS = True  # If true, it will try to check if two different uris have the same meaning
MAPPINGS_FILE_PATH = '/Users/marcosmr/tmp/ARM_resources/annotation_results/mappings.json'

READ_TEST_INSTANCES_FROM_CEDAR = False  # If false, the instances are read from a local folder
VR_SERVER = 'https://valuerecommender.metadatacenter.orgx/'
NCBI_TEMPLATE_ID = 'https://repo.metadatacenter.orgx/templates/eef6f399-aa4e-4982-ab04-ad8e9635aa91'
EBI_TEMPLATE_ID = 'https://repo.metadatacenter.orgx/templates/6b6c76e6-1d9b-4096-9702-133e25ecd140'
UNIQUE_VALUES_ANNOTATED_FILE_PATH = '/Users/marcosmr/tmp/ARM_resources/annotation_results/unique_values_annotated.txt'

# Output
EXPORT_RESULTS_PATH = '/Users/marcosmr/tmp/ARM_resources/evaluation_results'

# Relevant fields, with their paths and json path expressions
NCBI_FIELD_DETAILS = {'sex': {'path': 'sex', 'json_path': '$.sex'},
                      'tissue': {'path': 'tissue', 'json_path': '$.tissue'},
                      'cell_line': {'path': 'cell_line', 'json_path': '$.cell_line'},
                      'cell_type': {'path': 'cell_type', 'json_path': '$.cell_type'},
                      'disease': {'path': 'disease', 'json_path': '$.disease'},
                      'ethnicity': {'path': 'ethnicity', 'json_path': '$.ethnicity'}}

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

NCBI_TO_EBI_MAPPINGS = {
    'sex': 'sex',
    'tissue': 'organismPart',
    'cell_line': 'cellLine',
    'cell_type': 'cellType',
    'disease': 'diseaseState',
    'ethnicity': 'ethnicity'
}

# Note that I have mapped 'tissue' to 'organism part' because in EBI they use organism part and explain that it
# refers to the general location on the organism rather than a particular tissue (https://www.ebi.ac.uk/biosamples/help/st_scd)
STANDARD_FIELD_NAMES_FOR_PLOTS = {
    'sex': 'sex', 'tissue': 'organism part', 'cell_line': 'cell line', 'cell_type': 'cell type', 'disease': 'disease',
    'ethnicity': 'ethnicity',
    'sex': 'sex', 'organismPart': 'tissue', 'organism part': 'cell line', 'cellType': 'cell type', 'diseaseState': 'disease'
}


def get_mapped_field_path(field_name, training_db=TRAINING_DB, testing_db=TESTING_DB,
                          ebi_to_ncbi_mappings=EBI_TO_NCBI_MAPPINGS,
                          ncbi_to_ebi_mappings=NCBI_TO_EBI_MAPPINGS,
                          ncbi_field_details=NCBI_FIELD_DETAILS,
                          ebi_field_details=EBI_FIELD_DETAILS):
    if training_db == BIOSAMPLES_DB.NCBI:
        if testing_db == BIOSAMPLES_DB.NCBI:
            return ncbi_field_details[field_name]['path']
        elif testing_db == BIOSAMPLES_DB.EBI:
            mapped_field_name = ebi_to_ncbi_mappings[field_name]
            return ncbi_field_details[mapped_field_name]['path']

    elif training_db == BIOSAMPLES_DB.EBI:
        if testing_db == BIOSAMPLES_DB.EBI:
            return ebi_field_details[field_name]['path']
        elif testing_db == BIOSAMPLES_DB.NCBI:
            mapped_field_name = ncbi_to_ebi_mappings[field_name]
            if mapped_field_name in ebi_field_details:
                return ebi_field_details[mapped_field_name]['path']
            else:
                return None


def get_mapped_populated_fields(field_details, fields_types_and_values, target_field):
    """
    Returns the populated fields body, given the target field
    :param field_details: 
    :param field_values: 
    :param target_field: 
    :return: 
    """
    populated_fields = []
    for f in fields_types_and_values:
        if f != target_field:
            if fields_types_and_values[f]['value'] is not None:
                if fields_types_and_values[f]['type'] is not None:  # ontology term
                    path = fields_types_and_values[f]['type']
                    populated_fields.append({'path': path, 'value': fields_types_and_values[f]['value']})
                else:
                    mapped_field_path = get_mapped_field_path(field_details[f]['path'])
                    if mapped_field_path is None:
                        return None
                    populated_fields.append({'path': mapped_field_path, 'value': fields_types_and_values[f]['value']})
    return populated_fields


def get_baseline_top3_recommendation(field_name, training_db=TRAINING_DB, testing_db=TESTING_DB,
                                     ncbi_frequent_values=arm_constants.NCBI_MOST_FREQUENT_VALUES,
                                     ebi_frequent_values=arm_constants.EBI_MOST_FREQUENT_VALUES,
                                     ncbi_frequent_values_annotated=arm_constants.NCBI_MOST_FREQUENT_VALUES_ANNOTATED,
                                     ebi_frequent_values_annotated=arm_constants.EBI_MOST_FREQUENT_VALUES_ANNOTATED,
                                     annotated_values=ANNOTATED_VALUES):
    if annotated_values:
        ncbi_frequent_values = ncbi_frequent_values_annotated
        ebi_frequent_values = ebi_frequent_values_annotated

    if training_db == BIOSAMPLES_DB.NCBI:
        if testing_db == BIOSAMPLES_DB.NCBI:
            return ncbi_frequent_values[field_name]
        elif testing_db == BIOSAMPLES_DB.EBI:
            mapped_field_name = EBI_TO_NCBI_MAPPINGS[field_name]
            return ncbi_frequent_values[mapped_field_name]

    elif training_db == BIOSAMPLES_DB.EBI:
        if testing_db == BIOSAMPLES_DB.EBI:
            return ebi_frequent_values[field_name]
        elif testing_db == BIOSAMPLES_DB.NCBI:
            mapped_field_name = NCBI_TO_EBI_MAPPINGS[field_name]
            if mapped_field_name in ebi_frequent_values:
                return ebi_frequent_values[mapped_field_name]
            else:
                return None


def generate_populated_fields_sets(populated_fields, include_empty_list=True):
    """
    Generates all subsets of populated fields to be able to get recommendations from 0 populated fields to the max 
    number of populated fields in the instance
    :param populated_fields: 
    :param include_empty_list: 
    """
    pf_len = len(populated_fields)
    if include_empty_list:
        all_subsets = [[]]
    else:
        all_subsets = []  # We add the empty list to test the case when there are no populated fields

    for i in range(1, pf_len + 1):
        current_subsets = list(itertools.combinations(populated_fields, i))

        all_subsets = all_subsets + current_subsets

    return all_subsets


def main():
    # Read api key from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("apiKey", help="Your CEDAR apiKey")
    args = parser.parse_args()
    api_key = args.apiKey

    if ANNOTATED_VALUES and EXTEND_URIS_WITH_MAPPINGS:
        actually_extend_with_mappings = True
        mappings = json.load(open(MAPPINGS_FILE_PATH))

    results_database = []
    results_instance_ids = []
    results_populated_fields = []
    results_populated_fields_size = []
    results_field_names = []
    results_field_names_std = [] # standard field names, used for plots
    results_expected_values = []
    results_top1_values_vr = []
    results_top1_values_baseline = []
    results_correct_recommendations_vr = []
    results_correct_recommendations_baseline = []
    results_top3_values_vr = []
    results_top3_values_baseline = []
    results_reciprocal_rank_vr = []
    results_reciprocal_rank_vr_no_na = []
    results_reciprocal_rank_baseline = []
    results_exec_times_vr = []
    start_time = time.time()

    instances_count = 1

    if TESTING_DB == BIOSAMPLES_DB.NCBI:
        field_details = NCBI_FIELD_DETAILS
    elif TESTING_DB == BIOSAMPLES_DB.EBI:
        field_details = EBI_FIELD_DETAILS

    if TRAINING_DB == BIOSAMPLES_DB.NCBI and TESTING_DB == BIOSAMPLES_DB.NCBI:
        template_id = NCBI_TEMPLATE_ID
    elif TRAINING_DB == BIOSAMPLES_DB.EBI and TESTING_DB == BIOSAMPLES_DB.EBI:
        template_id = EBI_TEMPLATE_ID
    else:
        template_id = None

    test_instances_base_folder = arm_evaluation_util.get_testing_instances_folder(TRAINING_DB, TESTING_DB,
                                                                                  ANNOTATED_VALUES)

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
                    fields_types_and_values = arm_evaluation_util.get_instance_fields_types_and_values(instance_json,
                                                                                                       field_details)
                    for field_name in fields_types_and_values:
                        if fields_types_and_values[field_name]['value'] is not None:  # if the field is not empty

                            field_name_full = field_name
                            if fields_types_and_values[field_name]['type'] is not None:  # ontology term
                                field_path = fields_types_and_values[field_name]['type']
                                field_name_full = "[" + field_path + "](" + field_name + ")"
                            else:
                                field_path = get_mapped_field_path(field_name)

                            # Extract populated fields considering that fv is the target field
                            instance_populated_fields = get_mapped_populated_fields(field_details,
                                                                                    fields_types_and_values,
                                                                                    field_name)

                            populated_fields_sets = generate_populated_fields_sets(instance_populated_fields, True)

                            if field_path is not None and len(populated_fields_sets) > 0:

                                for populated_fields in populated_fields_sets:
                                    # Run the value recommender for the given field and populated fields
                                    start_time_vr = time.time()

                                    recommendation_vr = cedar_util.get_value_recommendation(VR_SERVER, template_id,
                                                                                            field_path,
                                                                                            populated_fields,
                                                                                            api_key, VR_STRICT_MATCH)
                                    execution_time_vr = int(round((time.time() - start_time_vr) * 1000))

                                    recommended_top1_value_vr = arm_evaluation_util.get_recommended_values(
                                        recommendation_vr, 1)

                                    recommended_top1_value_baseline = get_baseline_top3_recommendation(field_name)[0]

                                    is_correct_vr = arm_evaluation_util.get_matching_score(
                                        fields_types_and_values[field_name]['value'],
                                        arm_evaluation_util.get_recommended_values_as_string(recommended_top1_value_vr),
                                        mappings,
                                        extend_with_mappings=actually_extend_with_mappings)

                                    is_correct_baseline = arm_evaluation_util.get_matching_score(
                                        fields_types_and_values[field_name]['value'],
                                        recommended_top1_value_baseline,
                                        mappings,
                                        extend_with_mappings=actually_extend_with_mappings)

                                    recommended_top3_values_vr = arm_evaluation_util.get_recommended_values(
                                        recommendation_vr, 3)

                                    recommended_top3_values_baseline = get_baseline_top3_recommendation(field_name)

                                    reciprocal_rank_vr = arm_evaluation_util.reciprocal_rank(
                                        fields_types_and_values[field_name]['value'],
                                        recommended_top3_values_vr,
                                        mappings,
                                        extend_with_mappings=actually_extend_with_mappings)

                                    reciprocal_rank_baseline = arm_evaluation_util.reciprocal_rank(
                                        fields_types_and_values[field_name]['value'],
                                        recommended_top3_values_baseline,
                                        mappings,
                                        extend_with_mappings=actually_extend_with_mappings)

                                    # this is the reciprocal rank with 0s instead of NAs
                                    reciprocal_rank_vr_no_na = arm_evaluation_util.reciprocal_rank(
                                        fields_types_and_values[field_name]['value'],
                                        recommended_top3_values_vr,
                                        mappings,
                                        use_na=False,
                                        extend_with_mappings=actually_extend_with_mappings)

                                    # Store results in arrays
                                    instance_id = instances_count  # There is no id for instances read from a local folder so we just store the count
                                    results_instance_ids.append(instance_id)
                                    results_database.append(TESTING_DB.name)
                                    results_populated_fields.append(
                                        arm_evaluation_util.populated_fields_to_string(populated_fields))
                                    results_populated_fields_size.append(str(len(populated_fields)))
                                    results_field_names.append(field_name_full)
                                    results_field_names_std.append(STANDARD_FIELD_NAMES_FOR_PLOTS[field_name])
                                    results_expected_values.append(fields_types_and_values[field_name]['value'])
                                    results_top1_values_vr.append(
                                        arm_evaluation_util.get_recommended_values_as_string(recommended_top1_value_vr))
                                    results_top1_values_baseline.append(recommended_top1_value_baseline)
                                    results_correct_recommendations_vr.append(is_correct_vr)
                                    results_correct_recommendations_baseline.append(is_correct_baseline)
                                    results_top3_values_vr.append(
                                        arm_evaluation_util.get_recommended_values_as_string(
                                            recommended_top3_values_vr))
                                    results_top3_values_baseline.append(
                                        arm_evaluation_util.get_recommended_values_as_string(
                                            recommended_top3_values_baseline))
                                    results_reciprocal_rank_vr.append(reciprocal_rank_vr)
                                    results_reciprocal_rank_vr_no_na.append(reciprocal_rank_vr_no_na)
                                    results_reciprocal_rank_baseline.append(reciprocal_rank_baseline)
                                    results_exec_times_vr.append(execution_time_vr)

                            else:
                                print('Not doing anything for field: ' + field_name)

                    instances_count = instances_count + 1
                    if (instances_count % 100 == 0):
                        print('No. instances processed: ' + str(instances_count))

        # Stack the 1-D arrays generated as columns into a 2-D array
        results = np.column_stack(
            (results_database, results_instance_ids, results_populated_fields, results_populated_fields_size,
             results_field_names, results_field_names_std, results_expected_values, results_top1_values_vr, results_top1_values_baseline,
             results_correct_recommendations_vr, results_correct_recommendations_baseline,
             results_top3_values_vr, results_top3_values_baseline, results_reciprocal_rank_vr,
             results_reciprocal_rank_vr_no_na, results_reciprocal_rank_baseline,
             results_exec_times_vr))

        results_df = pd.DataFrame(results,
                                  columns=['database', 'instance_id', 'populated_fields', 'populated_fields_size',
                                           'target_field', 'target_field_std', 'expected_value', 'top1_value_vr', 'top1_value_baseline',
                                           'is_correct_vr', 'is_correct_baseline', 'top3_values_vr',
                                           'top3_values_baseline', 'RR_vr', 'RR_vr_no_NA', 'RR_baseline',
                                           'exec_time_vr'])

        print("\nExecution time:  %s seconds " % (time.time() - start_time))

        # Export results
        current_time = time.strftime("%Y-%m-%d_%H_%M_%S", time.gmtime())
        # results_path = EXPORT_RESULTS_PATH + '/' + current_time
        results_path = EXPORT_RESULTS_PATH
        if not os.path.exists(results_path):
            os.makedirs(results_path)

        # to CSV
        results_df.to_csv(
            results_path + '/' + 'results_train-' + TRAINING_DB.name + '_instances_test-' + TESTING_DB.name +
            '_' + str(instances_count - 1) + 'instances_' + current_time + '.csv',
            index=False, header=True)

        # Analysis of results
        # results_analysis.analyze_results(results_df)


if __name__ == "__main__": main()
