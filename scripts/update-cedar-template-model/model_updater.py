#!/usr/bin/python

# Created: 2016-Aug-16
# Last update: 2016-Aug-16
# model_updater.py: Utility to update CEDAR resources stored in a MongoDB database

import json

# import os.path
# import uuid
# import time
# import datetime
import sys
from pymongo import MongoClient
from pprint import pprint
from jsonpath_rw import jsonpath, parse
# from easydict import EasyDict as edict

### FUNCTION definitions ###

def __getattr__(self, name):
        return self[name]

def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True
    """

    if prompt is None:
        prompt = 'Confirm'

    prompt = '%s [%s/%s]: ' % (prompt, 'y', 'n')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def rename_field_jsonpath(tree, json_path, old_name, new_name):
    """renames all matching json fields using jsonpath notation"""
    jsonpath_expr = parse(json_path)
    matches = jsonpath_expr.find(tree)
    for m in matches:
        rename_field_dot_notation(tree, str(m.full_path), old_name, new_name)

def delete_field_jsonpath(tree, json_path, field_name):
    """deletes all matching json fields using jsonpath notation"""
    jsonpath_expr = parse(json_path)
    matches = jsonpath_expr.find(tree)
    for m in matches:
        delete_field_dot_notation(tree, str(m.full_path), field_name)

def rename_field_dot_notation(tree, path, old_name, new_name):
    """renames a json field using dot notation
    Input: 
    - json tree
    - path using dot notation (e.g., 'person.name.firstName')
    - current field name (only when path is an array)
    - new name for the field"""
    tmp = tree
    path_list = path.split(".")
    enum = enumerate(path_list)
    # Set tmp to be the last object in the path
    for i, p in enum:
        # Loop while i < sizeOfList - 1
        if (i+1)>=len(path_list):
            break

        if type(tmp) is not list:
            tmp = tmp[p]
        else:
            # Option 1: Array of objects (e.g. [ {...}, {...}, {...} ])
            # - If there is a position in the path after the array, we assume that it will be an object
            if (i+1) < len(path_list):
                current_pos = path_list[i]
                next_pos = path_list[i+1]
                # access to the array position (e.g., x in [x])
                position = int(current_pos[1:-1])
                tmp = tmp[position]
                # next(enum)
                # print('Moved to next!!!')
            # Option 1: Array of strings (e.g. ["a", "b", "c"])
            # - Do nothing here, the code below will take care of this option
    
    if type(tmp) is list:
        if old_name in tmp:
            tmp.remove(old_name)
            tmp.append(new_name)
            print('  - Renamed: ' + path + '(' + old_name + ') to ' + path + '(' + new_name + ')')
    else:
        # Note that path_list[-1] is the last element in the list
        tmp[new_name]=tmp[path_list[-1]] 
        del tmp[path_list[-1]]
        print('  - Renamed: ' + path + ' to ' + new_name)

def delete_field_dot_notation(tree, path, field_name):
    """deletes a json field using dot notation""" 
    path_list = path.split(".")
    tmp = tree
    for i in range(0,len(path_list)-1):
        tmp = tmp[path_list[i]]
    if type(tmp) is list:
        if field_name in tmp:
            tmp.remove(field_name)
            print('  - Deleted: ' + path + '(' + field_name + ')')
    else:
        del tmp[path_list[-1]]
        print('  - Deleted: ' + path)

def update_value_field(resource, resource_type):
    """Updates the value field from _value to the JSON-LD @value"""

    if (resource_type == TEMPLATE_TYPE or resource_type == ELEMENT_TYPE or resource_type == FIELD_TYPE or resource_type == STATIC_FIELD_TYPE) :
        # Delete @context._value
        delete_field_jsonpath(resource, '$..@context._value', None)
        # Delete @context.properties._value
        delete_field_jsonpath(resource, '$..@context.properties._value', None)
        # Delete _value in @context.required array
        delete_field_jsonpath(resource, '$..@context.required[:]', '_value')
        # Update properties._value to properties.@value
        rename_field_jsonpath(resource, '$..properties._value', None, '@value')
        # Update required array containing _value to contain @value
        rename_field_jsonpath(resource, '$..required[:]', '_value', '@value')
    elif (resource_type == INSTANCE_TYPE):
        # Delete @context._value
        delete_field_jsonpath(resource, '$..@context._value', None)
        # Update _value to @value
        rename_field_jsonpath(resource, '$.._value', None, '@value')
    else:
        raise Exception('Invalid resource type')

def update_model(resource, index, total):
    """This is the main method to update the CEDAR Template Model"""

    if '@type' in resource:
        resource_type = resource['@type'].rsplit('/', 1)[-1]
    else:
        resource_type = INSTANCE_TYPE
    
    resource_id = resource['@id']
    
    print('Resource: ' + resource_type + ' (id: ' + resource_id + ') (' + str(index) + '/' + str(total) + ')')
    print(' Updating _value to @value...')
    update_value_field(resource, resource_type)

### end of FUNCTION definitions ###

# Constants
VERSION = '08-16-2016'
DB_NAME = 'cedar'
UPDATED_DB_NAME = DB_NAME + '-updated'
OLD_DB_NAME = DB_NAME + '-old'
TEMPLATES_COLLECTION = 'templates'
ELEMENTS_COLLECTION = 'template-elements'
FIELDS_COLLECTION = 'template-fields'
INSTANCES_COLLECTION = 'template-instances'
TEMPLATE_TYPE = 'Template'
ELEMENT_TYPE = 'TemplateElement'
FIELD_TYPE = 'TemplateField'
STATIC_FIELD_TYPE = 'StaticTemplateField'
INSTANCE_TYPE = 'TemplateInstance'
RESOURCE_COLLECTIONS = [TEMPLATES_COLLECTION, ELEMENTS_COLLECTION, FIELDS_COLLECTION, INSTANCES_COLLECTION]

### Main program ###
print(' -------------------------------------------')
print('| CEDAR Template Model Updater v.' + VERSION + ' |')
print(' -------------------------------------------')
choice = confirm('WARNING: Running this script may affect the CEDAR resources stored in your local MongoDB database. The changes will be permanent.\nDo you want to continue?', False)
if choice is True:
    client = MongoClient()
    dbnames = client.database_names()

    if DB_NAME not in dbnames:
        raise Exception('Database \'' + DB_NAME + '\' does not exist')

    # Drop the 'updated' DB if it is there
    if UPDATED_DB_NAME in dbnames:
        print('Dropping the \'' + UPDATED_DB_NAME + '\' database')
        client.drop_database(UPDATED_DB_NAME)

    # Create copy of DB
    print('Creating copy of the \'' + DB_NAME + '\' database. New database: \'' + UPDATED_DB_NAME + '\'')
    client.admin.command('copydb', fromdb=DB_NAME, todb=UPDATED_DB_NAME)

    db = client[UPDATED_DB_NAME]
    
    resources_number = {}
    for collection in RESOURCE_COLLECTIONS:
        resources = db[collection].find()
        resources_number[collection] = resources.count()
        j=0
        for resource in resources:
            j=j+1
            update_model(resource, j, resources_number[collection])
            # Replace document in the DB with the updated version
            db[collection].replace_one({'_id':resource['_id']}, resource)

    print('\nDone! Number of resources updated:')
    for n in resources_number: 
        print('   ' + n + ': ' + str(resources_number[n]))
    print('\nThe updated resources have been stored into the \'' + UPDATED_DB_NAME + '\' database')

    choice = confirm('Do you want to rename the DBs as follows?\n 1)\'' + DB_NAME + '\' to \'' + OLD_DB_NAME + '\'\n 2)\'' + UPDATED_DB_NAME + '\' to \'' + DB_NAME + '\'\n', False)

    if choice is True:
        # rename DB_NAME to OLD_DB_NAME
        print('Renaming \'' + DB_NAME + '\' to \'' + OLD_DB_NAME + '\'...')
        client.drop_database(OLD_DB_NAME)
        client.admin.command('copydb', fromdb=DB_NAME, todb=OLD_DB_NAME)
        client.drop_database(DB_NAME)
        # rename UPDATED_DB_NAME to DB_NAME
        print('Renaming \'' + UPDATED_DB_NAME + '\' to \'' + DB_NAME + '\'...')
        client.admin.command('copydb', fromdb=UPDATED_DB_NAME, todb=DB_NAME)
        client.drop_database(UPDATED_DB_NAME)
        print('Finished renaming the DBs')















