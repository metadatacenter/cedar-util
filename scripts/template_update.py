#!/usr/bin/python

# 2015-Dec-15
# template_update.py: Utility to update the Investigation template to the "Template Model" specification available at December 15, 2015.

import json
import sys
import os.path
import uuid
import time
import datetime

from pprint import pprint

### FUNCTIONS ###

def update_name(tree, old_k, new_k):
    restart = True
    while restart:
        restart = False
        if type(tree) is list:
            for item in tree:
                if type(item) is dict or type(item) is list:
                   update_name(item, old_k, new_k)
                elif isinstance(item, basestring):
                    if item == old_k:
                        tree[tree.index(item)] = new_k
                        restart = True
        else:
            for key in tree.keys():
                if key == old_k:
                    #print(key + ' -> ' + new_k)
                    tree[new_k] = tree[old_k]
                    del tree[old_k]
                    restart = True
                elif type(tree[key]) is dict or type(tree[key]) is list:
                    update_name(tree[key], old_k, new_k)

# Moves field into a field_container
def move_order_and_pages_into_ui(tree):
    restart = True
    while restart:
        restart = False
        if type(tree) is list:
            for item in tree:
                if type(item) is dict or type(item) is list:
                   move_order_and_pages_into_ui(item)
        else:
            for key in tree.keys():
                if key == 'order' or key=='pages':
                    if len(tree.keys()) > 1:
                        # print(len(tree.keys()))
                        # print('type' in tree.keys())
                        # print(tree.keys())
                        tree['_ui'] = {}
                        tree['_ui'][key] = tree[key]
                        del tree[key]
                        restart = True
                else:
                    if type(tree[key]) is dict or type(tree[key]) is list:
                        move_order_and_pages_into_ui(tree[key])

# Move 'requiredValue' from '_ui' to '_valueConstraints'
def move_required_value(tree, parent_tree):
    restart = True
    while restart:
        restart = False
        if type(tree) is list:
            for item in tree:
                if type(item) is dict or type(item) is list:
                   move_required_value(item, tree)
        else:
            for key in tree.keys():
                if key == 'requiredValue':
                    if ('createdAt' in tree.keys()):
                        if ('_valueConstraints' not in parent_tree):
                            parent_tree['_valueConstraints'] = {}
                        parent_tree['_valueConstraints'][key] = tree[key]
                        del tree[key]
                        restart = True
                else:
                    if type(tree[key]) is dict or type(tree[key]) is list:
                        move_required_value(tree[key], tree)

# Move 'valueConstraints' outside of '_ui' field
def move_value_constraints(tree, parent_tree):
    restart = True
    while restart:
        restart = False
        if type(tree) is list:
            for item in tree:
                if type(item) is dict or type(item) is list:
                   move_value_constraints(item, tree)
        else:
            for key in tree.keys():
                if key == '_valueConstraints':
                    if ('createdAt' in tree.keys()):
                        if ('_valueConstraints' not in parent_tree):
                            parent_tree['_valueConstraints'] = {}
                        for k2 in tree[key].keys():
                            parent_tree['_valueConstraints'][k2] = tree[key][k2]
                        del tree[key]
                        restart = True
                else:
                    if type(tree[key]) is dict or type(tree[key]) is list:
                        move_value_constraints(tree[key], tree)


# Move _ui.title and _ui.description to schema:name and schema:description
def move_title_and_description(tree, parent_tree):
    restart = True
    while restart:
        restart = False
        if type(tree) is list:
            for item in tree:
                if type(item) is dict or type(item) is list:
                    move_title_and_description(item, tree)
        else:
            for key in tree.keys():
                if key == '_ui':
                    if 'title' in tree[key].keys():
                        tree['schema:name'] = tree[key]['title']
                        del tree[key]['title']
                        tree['schema:description'] = tree[key]['description']
                        del tree[key]['description']
                        restart = True
                else:
                    if type(tree[key]) is dict or type(tree[key]) is list:
                        move_title_and_description(tree[key], tree)


def insert_schema_version(tree, version):
    tree["schema:schemaVersion"] = version

###

if len(sys.argv) != 2:
    print('Please use the syntax: template_update.py template_file.json')
else:
    print('Updating template...')
    
    with open(sys.argv[1]) as input_file:
        input_file_name = sys.argv[1]
        data = json.load(input_file)
    
    output = data
    #
    # update_name(output, 'info', '_ui');
    # update_name(output, 'min_length', 'minLength');
    # update_name(output, 'max_length', 'maxLength');
    # update_name(output, 'default_option', 'defaultOption');
    # update_name(output, 'selection_type', 'selectionType');
    # update_name(output, 'warning_text', 'warningText');
    # update_name(output, 'date_type', 'dateType');
    # update_name(output, 'creation_date', 'creationDate');
    # update_name(output, 'template_description', 'templateDescription');
    # update_name(output, 'template_title', 'templateTitle');
    # update_name(output, 'value_sets', 'valueSets');
    # update_name(output, 'multiple_choice', 'multipleChoice');
    # update_name(output, 'created_at', 'createdAt');
    # update_name(output, 'input_type', 'inputType');
    # update_name(output, 'required_value', 'requiredValue');
    # update_name(output, 'max_depth', 'maxDepth');
    # update_name(output, 'value_constraint', '_valueConstraints');
    # update_name(output, '_value_label', 'valueLabel');
    # update_name(output, 'template_id', 'templateId');
    #
    #
    # move_order_and_pages_into_ui(output)
    #
    # # Move 'valueConstraints' outside of '_ui' field
    # move_value_constraints(output, None)
    #
    # # Move 'requiredValue' from '_ui' to '_valueConstraints'
    # move_required_value(output, None)

    insert_schema_version(output, "1.3.0")

    move_title_and_description(output, None)

    output_file_path = (os.path.splitext(input_file_name))[0] + '_updated.json'
    with open(output_file_path, 'w') as output_file:
        json.dump(output, output_file, indent=2)
    
    print(output_file_path)
