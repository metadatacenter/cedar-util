#!/usr/bin/python

# Created:      Mar-2-2017
# Last updated: Mar-3-2017
# evaluation_main.py: Utility to perform the evaluation for the AMIA2017 CEDAR paper.

import os
import random
import time

import numpy as np
import pandas as pd

import cedar_util
import evaluation_util
import results_analysis
import util
import elasticsearch_util as es

# CONSTANTS DEFINITION

# Constants used for instances retrieval
RESOURCE_SERVER = "https://resource.metadatacenter.orgx/"
VR_SERVER = "https://valuerecommender.metadatacenter.orgx/"
API_KEY = "<api_key>"
TEMPLATE_ID = "https://repo.metadatacenter.orgx/templates/f8b15441-bf39-4d4a-acd9-c98b4c972a40"
LIMIT_PER_CALL = 500
MAX_COUNT = 35157
TESTING_SET_SIZE = 7031
CONTEXT_ENABLED = True
CHECK_ALL_FIELDS_FILLED_OUT = False
REMOVE_TESTING_FROM_INDEX = True


def main():

    start_time = time.time()

    print('Retrieving instance ids...')
    instance_ids = cedar_util.get_template_instances_ids(RESOURCE_SERVER, TEMPLATE_ID, MAX_COUNT, LIMIT_PER_CALL, API_KEY)
    print('Done. ' + str(len(instance_ids)) + ' ids retrieved')
    print('Selecting instance ids...')
    selected_instance_ids = random.sample(instance_ids, TESTING_SET_SIZE)
    print('Done. ' + str(len(selected_instance_ids)) + ' ids selected')

    choice = True
    if REMOVE_TESTING_FROM_INDEX:
        choice = util.confirm('The selected instances will be removed from the index. Do you want to continue?', False)
        if choice is True:
            print('Removing instances from index...')
            for instance_id in selected_instance_ids:
                es.remove_instance_by_id(instance_id)

    if choice is True:
        # Run the Value Recommender for each instance and field of interest
        populated_fields = None
        results_instance_ids = []
        results_fields = []
        results_expected_values = []
        results_top1_values_baseline = []
        results_correct_recommendations_baseline = []
        results_top1_values_vr = []
        results_correct_recommendations_vr = []
        results_top3_values_baseline = []
        results_reciprocal_rank_baseline = []
        results_top3_values_vr = []
        results_reciprocal_rank_vr = []
        results_exec_times_baseline = []
        results_exec_times_vr = []

        count = 0

        for instance_id in selected_instance_ids:
            count += 1
            print('Processing instance no. ' + str(count))
            field_values = evaluation_util.get_instance_fields_values(RESOURCE_SERVER, instance_id, API_KEY)
            # Check that all fields contain values
            # if evaluation_util.all_filled_out(field_values):
            skip = False
            if CHECK_ALL_FIELDS_FILLED_OUT:
                if not evaluation_util.all_filled_out(field_values):
                    skip = True
            if not skip:
                for f in field_values:
                    if CONTEXT_ENABLED:
                        populated_fields = evaluation_util.get_populated_fields(field_values, f)
                    else:
                        populated_fields = None
                    field_path = evaluation_util.get_field_path(f)

                    start_time_baseline = time.time()
                    recommendation_baseline = cedar_util.get_value_recommendation(VR_SERVER, TEMPLATE_ID, field_path, None,
                                                                                  API_KEY)
                    execution_time_baseline = int(round((time.time() - start_time_baseline) * 1000))

                    start_time_vr = time.time()
                    recommendation_vr = cedar_util.get_value_recommendation(VR_SERVER, TEMPLATE_ID, field_path,
                                                                            populated_fields,
                                                                            API_KEY)
                    execution_time_vr = int(round((time.time() - start_time_vr) * 1000))

                    recommended_top1_value_baseline = evaluation_util.get_recommended_values(recommendation_baseline, 1)[0]
                    is_correct_baseline = evaluation_util.get_correct_score(field_values[f], recommended_top1_value_baseline)
                    recommended_top1_value_vr = evaluation_util.get_recommended_values(recommendation_vr, 1)[0]
                    is_correct_vr = evaluation_util.get_correct_score(field_values[f], recommended_top1_value_vr)

                    recommended_top3_values_baseline = evaluation_util.get_recommended_values(recommendation_baseline, 3)
                    reciprocal_rank_baseline = evaluation_util.reciprocal_rank(field_values[f], recommended_top3_values_baseline)
                    recommended_top3_values_vr = evaluation_util.get_recommended_values(recommendation_vr, 3)
                    reciprocal_rank_vr = evaluation_util.reciprocal_rank(field_values[f], recommended_top3_values_vr)

                    results_instance_ids.append(instance_id)
                    results_fields.append(f)
                    results_expected_values.append(field_values[f])

                    results_top1_values_baseline.append(recommended_top1_value_baseline)
                    results_correct_recommendations_baseline.append(is_correct_baseline)
                    results_top1_values_vr.append(recommended_top1_value_vr)
                    results_correct_recommendations_vr.append(is_correct_vr)

                    results_top3_values_baseline.append("|".join(recommended_top3_values_baseline))
                    results_reciprocal_rank_baseline.append(reciprocal_rank_baseline)
                    results_top3_values_vr.append("|".join(recommended_top3_values_vr))
                    results_reciprocal_rank_vr.append(reciprocal_rank_vr)

                    results_exec_times_baseline.append(execution_time_baseline)
                    results_exec_times_vr.append(execution_time_vr)

        # Stack the 1-D arrays generated as columns into a 2-D array
        results = np.column_stack((results_instance_ids, results_fields, results_expected_values,
                                   results_top1_values_baseline, results_correct_recommendations_baseline,
                                   results_top1_values_vr, results_correct_recommendations_vr,
                                   results_top3_values_baseline, results_reciprocal_rank_baseline,
                                   results_top3_values_vr, results_reciprocal_rank_vr, results_exec_times_baseline,
                                   results_exec_times_vr))

        results_df = pd.DataFrame(results, columns=['instance_id', 'field', 'expected_value',
                                                    'top1_value_baseline', 'correct_baseline',
                                                    'top1_value_vr', 'correct_vr',
                                                    'top3_values_baseline', 'RR_baseline',
                                                    'top3_values_vr', 'RR_vr', 'exec_time_baseline', 'exec_time_vr'])

        print("\nExecution time:  %s seconds " % (time.time() - start_time))

        # Export results
        current_time = time.strftime("%Y-%m-%d_%H_%M_%S", time.gmtime())
        folder_path = 'results/' + current_time
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # to CSV
        suffix = 'NoCheck'
        if CHECK_ALL_FIELDS_FILLED_OUT:
            suffix = 'Check'
        results_df.to_csv(folder_path + '/' + 'results_' + str(MAX_COUNT) + '_' + str(TESTING_SET_SIZE) + '_' + suffix + '.csv', index=False, header=True)

        # Analysis of results
        results_analysis.analyze_results(results_df)


if __name__ == "__main__": main()