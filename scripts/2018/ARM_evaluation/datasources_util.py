#!/usr/bin/python3

# Utilities to perform diverse operations on NCBI and EBI biosamples

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import urllib.parse
import os
from fnmatch import fnmatch


def is_valid_value(value):
    if value is None:
        return False
    else:
        invalid_values = ['na', 'n/a', 'not applicable', '?', '-', '--', 'unknown', 'missing', 'not collected',
                          'none', 'normal']
        value = value.lower().strip()
        if value not in invalid_values:
            return True
        else:
            # print('invalid value: ' + value)
            return False


def extract_ncbi_attribute_value(attribute_node, attribute_name):
    """
    It extracts the attribute value from a BioSample attribute XML node
    :param attribute_node: 
    :param attribute_name: 
    :return: The attribute value
    """
    value = None
    if attribute_node.get('attribute_name') == attribute_name \
            or attribute_node.get('harmonized_name') == attribute_name \
            or attribute_node.get('display_name') == attribute_name:
        value = attribute_node.text

    return value


def extract_ebi_value(sample, field_name):
    value = None
    if field_name in sample:
        field_type = type(sample[field_name])
        if field_type == str:
            value = sample[field_name]
        elif field_type == list:
            value_obj = sample[field_name][0]
            if 'text' in value_obj:
                value = value_obj['text']
            elif 'name' in value_obj:
                value = value_obj['name']
            elif 'Name' in value_obj:
                value = value_obj['Name']
    return value
