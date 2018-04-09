# Evaluation utils

import cedar_util
import string
from jsonpath_rw import jsonpath, parse
import json
import urllib.parse
from enum import Enum

MISSING_VALUE = 'NA'


class BIOSAMPLES_DB(Enum):
    NCBI = 1
    EBI = 2


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
            if '@value' in matches[0].value and  matches[0].value['@value'] is not None:
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
        return urllib.parse.unquote(encoded_term_uri) # return the decoded uri
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
    for rv in recommendation_results['recommendedValues']:
        recommended_values.append(rv['value'])
    result = recommended_values[:max_size]
    return result


def get_recommended_values_as_string(recommended_values):
    if len(recommended_values) == 0:
        return MISSING_VALUE
    elif len(recommended_values) == 1:
        return recommended_values[0]
    else:
        return "|".join(recommended_values)


def get_matching_score(expected_value, value, normalization=True):
    if value == MISSING_VALUE:
        return MISSING_VALUE
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
    field_value_pairs = []
    for pf in populated_fields:
        field_value_pairs.append(pf['path'] + '=' + pf['value'])
    return "|".join(field_value_pairs)


# Calculates the Reciprocal Rank (https://en.wikipedia.org/wiki/Mean_reciprocal_rank). The MRR will be computed later
def reciprocal_rank(expected_value, actual_values, use_na=True):
    if use_na and (actual_values == MISSING_VALUE or actual_values is None or len(actual_values) == 0):
        return MISSING_VALUE
    else:
        position = 1
        for value in actual_values:
            if value == expected_value:
                return 1 / float(position)
            position += 1
        return 0


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
