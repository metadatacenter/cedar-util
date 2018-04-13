# Evaluation utils

import cedar_util
import arm_constants
import string
from jsonpath_rw import jsonpath, parse
import json
import urllib.parse
from enum import Enum

MISSING_VALUE = 'NA'


def get_training_instances_folder(database, annotated_instances=False):
    if database == arm_constants.BIOSAMPLES_DB.NCBI:
        base = arm_constants.TRAINING_BASE_FOLDERS['NCBI']
    elif database == arm_constants.BIOSAMPLES_DB.EBI:
        base = arm_constants.TRAINING_BASE_FOLDERS['EBI']
    else:
        raise Exception('Invalid database')

    if annotated_instances:
        return base + "/" + arm_constants.TRAINING_INSTANCES_ANNOTATED_FOLDER_NAME
    else:
        return base + "/" + arm_constants.TRAINING_INSTANCES_FOLDER_NAME


def get_testing_instances_folder(training_database, testing_database, annotated_instances=False):
    if training_database == arm_constants.BIOSAMPLES_DB.NCBI:
        if testing_database == arm_constants.BIOSAMPLES_DB.NCBI:
            base = arm_constants.TESTING_BASE_FOLDERS['NCBI_NCBI']
        elif testing_database == arm_constants.BIOSAMPLES_DB.EBI:
            base = arm_constants.TESTING_BASE_FOLDERS['NCBI_EBI']
        else:
            raise Exception('Invalid database')
    elif training_database == arm_constants.BIOSAMPLES_DB.EBI:
        if testing_database == arm_constants.BIOSAMPLES_DB.NCBI:
            base = arm_constants.TESTING_BASE_FOLDERS['EBI_NCBI']
        elif testing_database == arm_constants.BIOSAMPLES_DB.EBI:
            base = arm_constants.TESTING_BASE_FOLDERS['EBI_EBI']
        else:
            raise Exception('Invalid database')
    else:
        raise Exception('Invalid database')

    if annotated_instances:
        return base + "/" + arm_constants.TESTING_INSTANCES_ANNOTATED_FOLDER_NAME
    else:
        return base + "/" + arm_constants.TESTING_INSTANCES_FOLDER_NAME


# Returns the instance fields (with their types and values) that are used for the evaluation as a Panda data frame
def get_instance_fields_types_and_values(instance, field_details):
    field_values = {}

    for field in field_details:
        jsonpath_expr = parse(field_details[field]['json_path'])
        matches = jsonpath_expr.find(instance)
        field_values[field] = {}
        field_values[field]['value'] = None
        field_values[field]['type'] = None
        if matches[0] is not None and matches[0].value is not None:
            if '@value' in matches[0].value and matches[0].value['@value'] is not None:
                field_values[field]['value'] = matches[0].value['@value']
            elif '@id' in matches[0].value and matches[0].value['@id'] is not None:
                field_values[field]['value'] = matches[0].value['@id']
            if '@type' in matches[0].value and matches[0].value['@type'] is not None:
                field_type = matches[0].value['@type']
                field_values[field]['type'] = get_original_term_uri(field_type)

    return field_values


# Get the original term uris from BioPortal URIs
def get_original_term_uri(field_type):
    substr = '/classes/'
    if substr in field_type:
        index = field_type.find(substr)
        encoded_term_uri = field_type[index + len(substr):]
        return urllib.parse.unquote(encoded_term_uri)  # return the decoded uri
    else:
        return field_type


def get_populated_fields(field_details, field_values, target_field):
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
                populated_fields.append({'path': field_details[f]['path'], 'value': field_values[f]})
    return populated_fields


# def get_field_path(field_name):
#     return field_paths[field_name]['path']


# Checks if all field values are filled out
def all_filled_out(field_values):
    for f in field_values:
        if field_values[f] is None or len(field_values[f]) == 0:
            return False
    return True


def get_recommended_values(recommendation_results, max_size):
    if max_size <= 0:
        raise ValueError("max_size must be > 0")
    recommended_values = []
    if 'recommendedValues' in recommendation_results:
        for rv in recommendation_results['recommendedValues']:
            recommended_values.append(rv['value'])
    else:
        print('Error: recommendedValues not found in recommendation_results')
    result = recommended_values[:max_size]
    return result


def get_recommended_values_as_string(recommended_values):
    if len(recommended_values) == 0:
        return MISSING_VALUE
    elif len(recommended_values) == 1:
        return recommended_values[0]
    else:
        return "|".join(recommended_values)


def is_same_concept(term_uri1, term_uri2, mappings):
    """
    Checks if two term uris have the same meaning. It makes use of a file with mappings
    :param term_uri1: 
    :param term_uri2: 
    """
    if term_uri1 == term_uri2:
        return True
    elif term_uri1 in mappings[term_uri2] or term_uri2 in mappings[term_uri1]:
        # print('Found two uris for the same concept: ' + term_uri1 + ' = ' + term_uri2)
        return True
    else:
        return False


def get_matching_score(expected_value, value, mappings, normalization=True, extend_with_mappings=False):
    if value == MISSING_VALUE:
        return MISSING_VALUE
    else:
        if extend_with_mappings:
            if is_same_concept(value, expected_value, mappings):
                return 1
            else:
                return 0
        else:
            if normalization:
                value = value.lower()
                expected_value = expected_value.lower()

                # Remove punctuation
                value = value.translate(str.maketrans('', '', string.punctuation))
                expected_value = expected_value.translate(str.maketrans('', '', string.punctuation))

            if expected_value == value:
                return 1
            else:
                return 0


def populated_fields_to_string(populated_fields):
    if len(populated_fields) == 0:
        return 'NA'
    field_value_pairs = []
    for pf in populated_fields:
        field_value_pairs.append(pf['path'] + '=' + pf['value'])
    return "|".join(field_value_pairs)


def position_of_expected_value(expected_value, values, mappings, extend_with_mappings=False):
    position = 1  # 1-based position
    for value in values:
        if get_matching_score(expected_value, value, mappings, extend_with_mappings) == 1:
            return position
        position += 1
    return 'NA'  # If not found


# Calculates the Reciprocal Rank (https://en.wikipedia.org/wiki/Mean_reciprocal_rank). The MRR will be computed later
def reciprocal_rank(number_of_positions, expected_value, actual_values, mappings, use_na=False,
                    extend_with_mappings=False):
    if use_na and (actual_values == MISSING_VALUE or actual_values is None or len(actual_values) == 0):
        return MISSING_VALUE
    else:
        values = actual_values[0, number_of_positions]
        position = 1
        for value in values:
            if get_matching_score(expected_value, value, mappings, extend_with_mappings) == 1:
                return 1 / float(position)
            position += 1
        return 0


# Note that position is 1-based
def reciprocal_rank_using_position(number_of_positions, position, use_na=False):
    if position is None or position is 'NA':
        if use_na:
            return MISSING_VALUE
        else:
            return 0
    else:
        if position > number_of_positions:
            return 0
        else:
            return 1 / float(position)


def save_to_folder(instance, instance_number, output_path, output_base_file_name):
    """
    Saves an instance to a local folder
    :param instance: 
    :param instance_number: Number used to name the output files
    :param output_path: 
    :param output_base_file_name:
    """
    output_file_path = output_path + "/" + output_base_file_name + "_" + str(instance_number) + '.json'

    with open(output_file_path, 'w') as output_file:
        json.dump(instance, output_file, indent=4)
