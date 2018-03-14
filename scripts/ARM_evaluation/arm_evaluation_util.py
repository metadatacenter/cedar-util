# Evaluation utils

import cedar_util
from jsonpath_rw import jsonpath, parse


# Returns the instance fields (with their values) that are used for the evaluation as a Panda data frame
def get_instance_fields_values(instance, field_details):
    field_values = {}

    for field in field_details:
        jsonpath_expr = parse(field_details[field]['json_path'])
        matches = jsonpath_expr.find(instance)
        field_values[field] = None
        if matches[0] is not None and matches[0].value['@value'] is not None:
            field_values[field] = matches[0].value['@value']

    return field_values


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
    recommended_values = []
    if len(recommendation_results['recommendedValues']) > 0:
        for rv in recommendation_results['recommendedValues']:
            recommended_values.append(rv['value'])
    result = recommended_values[:max_size]
    # result_string = "|".join(result)
    # return result_string
    return result


def get_correct_score(expected_value, actual_value):
    if expected_value == actual_value:
        return 1
    else:
        return 0


# Calculates the Reciprocal Rank (https://en.wikipedia.org/wiki/Mean_reciprocal_rank). The MRR will be computed later
def reciprocal_rank(expected_value, actual_values):
    position = 1
    for value in actual_values:
        if value == expected_value:
            return 1 / float(position)
        position += 1
    return 0
