#!/usr/bin/python3

# evaluation_main.py: Utility to perform the evaluation of the ARM-based metadata recommender

import itertools
import json
import os
import time

import arm_constants
import arm_evaluation_util
import cedar_util
import numpy as np
import pandas as pd
from arm_constants import BIOSAMPLES_DB

CEDAR_API_KEY = arm_constants.EVALUATION_CEDAR_API_KEY
# Input (Don't forget to regenerate the most frequent values from the ARFF files if needed)
TRAINING_DB = arm_constants.EVALUATION_TRAINING_DB
TESTING_DB = arm_constants.EVALUATION_TESTING_DB
VR_STRICT_MATCH = arm_constants.EVALUATION_VR_STRICT_MATCH
MAX_NUMBER_INSTANCES = arm_constants.EVALUATION_MAX_NUMBER_INSTANCES  # Max number of instances that will be part of the test set
ANNOTATED_VALUES = arm_constants.EVALUATION_USE_ANNOTATED_VALUES
EXTEND_URIS_WITH_MAPPINGS = arm_constants.EVALUATION_EXTEND_URIS_WITH_MAPPINGS  # If true, it will try to check if two different uris have the same meaning
MAPPINGS_FILE_PATH = arm_constants.EVALUATION_MAPPINGS_FILE_PATH
READ_TEST_INSTANCES_FROM_CEDAR = arm_constants.EVALUATION_READ_TEST_INSTANCES_FROM_CEDAR  # If false, the instances are read from a local folder
VR_SERVER = arm_constants.EVALUATION_VR_SERVER
NCBI_TEMPLATE_ID = arm_constants.EVALUATION_NCBI_TEMPLATE_ID
EBI_TEMPLATE_ID = arm_constants.EVALUATION_EBI_TEMPLATE_ID
# Output
EXPORT_RESULTS_PATH = arm_constants.EVALUATION_OUTPUT_RESULTS_PATH
# Relevant fields, with their paths and json path expressions
NCBI_FIELD_DETAILS = arm_constants.EVALUATION_NCBI_FIELD_DETAILS
EBI_FIELD_DETAILS = arm_constants.EVALUATION_EBI_FIELD_DETAILS
EBI_TO_NCBI_MAPPINGS = arm_constants.EVALUATION_EBI_TO_NCBI_MAPPINGS
NCBI_TO_EBI_MAPPINGS = arm_constants.EVALUATION_NCBI_TO_EBI_MAPPINGS
STANDARD_FIELD_NAMES_FOR_PLOTS = arm_constants.EVALUATION_STANDARD_FIELD_NAMES_FOR_PLOTS


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


def get_baseline_top10_recommendation(field_name,
                                      ncbi_frequent_values,
                                      ebi_frequent_values,
                                      ncbi_frequent_values_annotated,
                                      ebi_frequent_values_annotated,
                                      training_db=TRAINING_DB, testing_db=TESTING_DB,
                                      annotated_values=ANNOTATED_VALUES):

    if not annotated_values:
        ncbi_fv = ncbi_frequent_values
        ebi_fv = ebi_frequent_values
    else:
        ncbi_fv = ncbi_frequent_values_annotated
        ebi_fv = ebi_frequent_values_annotated

    if training_db == BIOSAMPLES_DB.NCBI:
        if testing_db == BIOSAMPLES_DB.NCBI:
            return ncbi_fv[field_name]
        elif testing_db == BIOSAMPLES_DB.EBI:
            mapped_field_name = EBI_TO_NCBI_MAPPINGS[field_name]
            return ncbi_fv[mapped_field_name]

    elif training_db == BIOSAMPLES_DB.EBI:
        if testing_db == BIOSAMPLES_DB.EBI:
            return ebi_fv[field_name]
        elif testing_db == BIOSAMPLES_DB.NCBI:
            mapped_field_name = NCBI_TO_EBI_MAPPINGS[field_name]
            if mapped_field_name in ebi_fv:
                return ebi_fv[mapped_field_name]
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
    # Read frequent values files, used for baseline recommendations
    ncbi_frequent_values = json.load(open(arm_constants.EVALUATION_NCBI_MOST_FREQUENT_VALUES_PATH))
    ebi_frequent_values = json.load(open(arm_constants.EVALUATION_EBI_MOST_FREQUENT_VALUES_PATH))
    ncbi_annotated_frequent_values = json.load(open(arm_constants.EVALUATION_NCBI_MOST_FREQUENT_VALUES_ANNOTATED_PATH))
    ebi_annotated_frequent_values = json.load(open(arm_constants.EVALUATION_EBI_MOST_FREQUENT_VALUES_ANNOTATED_PATH))

    if ANNOTATED_VALUES and EXTEND_URIS_WITH_MAPPINGS:
        actually_extend_with_mappings = True
        mappings = json.load(open(MAPPINGS_FILE_PATH))
    else:
        actually_extend_with_mappings = False
        mappings = {}

    results_database = []
    results_instance_ids = []
    results_populated_fields = []
    results_populated_fields_size = []
    results_field_names = []
    results_field_names_std = []  # standard field names, used for plots
    results_expected_values = []
    results_top1_values_vr = []
    results_top1_values_baseline = []
    results_correct_recommendations_vr = []
    results_correct_recommendations_baseline = []
    results_top10_values_vr = []
    results_top10_values_baseline = []
    results_correct_position_vr = []
    results_correct_position_baseline = []
    results_reciprocal_rank_top3_vr = []
    results_reciprocal_rank_top5_vr = []
    results_reciprocal_rank_top10_vr = []
    results_reciprocal_rank_top3_baseline = []
    results_reciprocal_rank_top5_baseline = []
    results_reciprocal_rank_top10_baseline = []
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

    test_instances_base_folder = arm_evaluation_util.get_test_instances_folder(TESTING_DB, ANNOTATED_VALUES)

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

                    if '@id' in instance_json:
                        instance_id = instance_json['@id']
                    else:
                        instance_id = 'NA'
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

                                    repeat = True
                                    while repeat:
                                        recommendation_vr = cedar_util.get_value_recommendation(VR_SERVER, template_id,
                                                                                                field_path,
                                                                                                populated_fields,
                                                                                                CEDAR_API_KEY,
                                                                                                VR_STRICT_MATCH)
                                        if 'recommendedValues' not in recommendation_vr:
                                            print('Error: recommendedValues not found in recommendation_results.')
                                            print('  The Value Recommender server or Elasticsearch may be down.')
                                            print('  Trying again in 5 seconds...')
                                            time.sleep(5)
                                        else:
                                            repeat = False

                                    execution_time_vr = int(round((time.time() - start_time_vr) * 1000))

                                    recommended_top1_value_vr = arm_evaluation_util.get_recommended_values(
                                        recommendation_vr, 1)

                                    baseline_top_10 = get_baseline_top10_recommendation(field_name,
                                                                                                        ncbi_frequent_values,
                                                                                                        ebi_frequent_values,
                                                                                                        ncbi_annotated_frequent_values,
                                                                                                        ebi_annotated_frequent_values)
                                    if baseline_top_10 is not None and len(baseline_top_10) > 0:
                                        recommended_top1_value_baseline = baseline_top_10[0]
                                    else:
                                        recommended_top1_value_baseline = 'NA'


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

                                    recommended_top10_values_vr = arm_evaluation_util.get_recommended_values(
                                        recommendation_vr, 10)

                                    recommended_top10_values_baseline = get_baseline_top10_recommendation(field_name,
                                                                                                          ncbi_frequent_values,
                                                                                                          ebi_frequent_values,
                                                                                                          ncbi_annotated_frequent_values,
                                                                                                          ebi_annotated_frequent_values)

                                    expected_value = fields_types_and_values[field_name]['value']

                                    position_of_expected_value_vr = arm_evaluation_util.position_of_expected_value(
                                        expected_value, recommended_top10_values_vr, mappings,
                                        extend_with_mappings=actually_extend_with_mappings)

                                    position_of_expected_value_baseline = arm_evaluation_util.position_of_expected_value(
                                        expected_value, recommended_top10_values_baseline, mappings,
                                        extend_with_mappings=actually_extend_with_mappings)

                                    reciprocal_rank_top3_vr = arm_evaluation_util.reciprocal_rank_using_position \
                                        (3, position_of_expected_value_vr, use_na=False)

                                    reciprocal_rank_top5_vr = arm_evaluation_util.reciprocal_rank_using_position \
                                        (5, position_of_expected_value_vr, use_na=False)

                                    reciprocal_rank_top10_vr = arm_evaluation_util.reciprocal_rank_using_position \
                                        (10, position_of_expected_value_vr, use_na=False)

                                    reciprocal_rank_top3_baseline = arm_evaluation_util.reciprocal_rank_using_position \
                                        (3, position_of_expected_value_baseline, use_na=False)

                                    reciprocal_rank_top5_baseline = arm_evaluation_util.reciprocal_rank_using_position \
                                        (5, position_of_expected_value_baseline, use_na=False)

                                    reciprocal_rank_top10_baseline = arm_evaluation_util.reciprocal_rank_using_position \
                                        (10, position_of_expected_value_baseline, use_na=False)

                                    # Store results in arrays
                                    results_instance_ids.append(instance_id)
                                    results_database.append(TESTING_DB.name)
                                    results_populated_fields.append(
                                        arm_evaluation_util.populated_fields_to_string(populated_fields))
                                    results_populated_fields_size.append(str(len(populated_fields)))
                                    results_field_names.append(field_name_full)
                                    results_field_names_std.append(STANDARD_FIELD_NAMES_FOR_PLOTS[field_name])
                                    results_expected_values.append(expected_value)
                                    results_top1_values_vr.append(
                                        arm_evaluation_util.get_recommended_values_as_string(recommended_top1_value_vr))
                                    results_top1_values_baseline.append(recommended_top1_value_baseline)
                                    results_correct_recommendations_vr.append(is_correct_vr)
                                    results_correct_recommendations_baseline.append(is_correct_baseline)
                                    results_top10_values_vr.append(
                                        arm_evaluation_util.get_recommended_values_as_string(
                                            recommended_top10_values_vr))
                                    results_top10_values_baseline.append(
                                        arm_evaluation_util.get_recommended_values_as_string(
                                            recommended_top10_values_baseline))
                                    results_correct_position_vr.append(position_of_expected_value_vr)
                                    results_correct_position_baseline.append(position_of_expected_value_baseline)
                                    results_reciprocal_rank_top3_vr.append(reciprocal_rank_top3_vr)
                                    results_reciprocal_rank_top5_vr.append(reciprocal_rank_top5_vr)
                                    results_reciprocal_rank_top10_vr.append(reciprocal_rank_top10_vr)
                                    results_reciprocal_rank_top3_baseline.append(reciprocal_rank_top3_baseline)
                                    results_reciprocal_rank_top5_baseline.append(reciprocal_rank_top5_baseline)
                                    results_reciprocal_rank_top10_baseline.append(reciprocal_rank_top10_baseline)
                                    results_exec_times_vr.append(execution_time_vr)

                            else:
                                print('Not doing anything for field: ' + field_name)

                    instances_count = instances_count + 1
                    if instances_count % 100 == 0:
                        print('No. instances processed: ' + str(instances_count))

        # Stack the 1-D arrays generated as columns into a 2-D array
        results = np.column_stack(
            (results_database, results_instance_ids, results_populated_fields, results_populated_fields_size,
             results_field_names, results_field_names_std, results_expected_values, results_top1_values_vr,
             results_top1_values_baseline,
             results_correct_recommendations_vr, results_correct_recommendations_baseline,
             results_top10_values_vr, results_top10_values_baseline,
             results_correct_position_vr, results_correct_position_baseline,
             results_reciprocal_rank_top3_vr, results_reciprocal_rank_top5_vr, results_reciprocal_rank_top10_vr,
             results_reciprocal_rank_top3_baseline, results_reciprocal_rank_top5_baseline,
             results_reciprocal_rank_top10_baseline,
             results_exec_times_vr))

        results_df = pd.DataFrame(results,
                                  columns=['database', 'instance_id', 'populated_fields', 'populated_fields_size',
                                           'target_field', 'target_field_std', 'expected_value', 'top1_value_vr',
                                           'top1_value_baseline',
                                           'is_correct_vr', 'is_correct_baseline', 'top10_values_vr',
                                           'top10_values_baseline',
                                           'correct_pos_vr', 'correct_pos_baseline',
                                           'RR_top3_vr', 'RR_top5_vr', 'RR_top10_vr',
                                           'RR_top3_baseline', 'RR_top5_baseline', 'RR_top10_baseline',
                                           'exec_time_vr'])

        print("\nExecution time:  %s seconds " % (time.time() - start_time))

        # Export results
        current_time = time.strftime("%Y-%m-%d_%H_%M_%S", time.gmtime())
        # results_path = EXPORT_RESULTS_PATH + '/' + current_time
        results_path = EXPORT_RESULTS_PATH
        if not os.path.exists(results_path):
            os.makedirs(results_path)

        # to CSV
        suffix = ''
        if ANNOTATED_VALUES:
            suffix = suffix + '_annotated'
        if actually_extend_with_mappings:
            suffix = suffix + '_mappings'
        results_df.to_csv(
            results_path + '/' + 'results_train' + TRAINING_DB.name + '_test' + TESTING_DB.name + suffix + '_' + current_time + '.csv',
            index=False, header=True)


if __name__ == "__main__": main()
