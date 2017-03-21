# Evaluation utils

import cedar_util
from jsonpath_rw import jsonpath, parse

# Relevant fields, with their paths and json path expressions
field_paths = {'tissue': {'path': 'tissue', 'json_path': '$.tissue'},
               'sex': {'path': 'sex', 'json_path': '$.sex'},
               'disease': {'path': 'optionalAttribute.value', 'json_path': '$.optionalAttribute'}}


# Returns the instance fields (with their values) that are used for the evaluation as a Panda data frame
def get_instance_fields_values(server, template_instance_id, api_key):
    # Retrieve instance content
    instance = cedar_util.get_template_instance_by_id(server, template_instance_id, api_key)

    field_values = {}

    for field in field_paths:
        jsonpath_expr = parse(field_paths[field]['json_path'])
        matches = jsonpath_expr.find(instance)
        if len(matches) == 0:
            field_value = None
        for match in matches:
            if field == 'disease':
                for optional_attribute in match.value:
                    if optional_attribute['name']['@value'] == 'disease':
                        value_object = optional_attribute['value']
            else:
                value_object = match.value

            if not value_object:
                field_value = None
            else:
                if '_valueLabel' in value_object:
                    field_value = value_object['_valueLabel']
                else:
                    field_value = value_object['@value']

            if field_value is not None:
                if len(field_value) == 0:
                    field_value = None
        field_values[field] = field_value

    return field_values


# Returns the populated fields body, given the target field
def get_populated_fields(field_values, target_field):
    populated_fields = []
    for f in field_values:
        if f != target_field:
            if field_values[f] is not None:
                populated_fields.append({'path': field_paths[f]['path'], 'value': field_values[f]})
    if target_field == 'disease':
        populated_fields.append({'path': 'optionalAttribute.name', 'value': 'disease'})
    return populated_fields


def get_field_path(field_name):
    return field_paths[field_name]['path']


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

#  Calculates the Reciprocal Rank (https://en.wikipedia.org/wiki/Mean_reciprocal_rank). The MRR will be computed later
def reciprocal_rank(expected_value, actual_values):
    position = 1
    for value in actual_values:
        if value == expected_value:
            return 1 / float(position)
        position += 1
    return 0