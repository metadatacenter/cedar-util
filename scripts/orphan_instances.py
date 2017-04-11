#!/usr/bin/python

# Created: 2016-Aug-16
# Last update: 2017-Feb-27
# model_updater.py: Utility to update CEDAR resources stored in a MongoDB database

import json
import sys
from pymongo import MongoClient
from pprint import pprint
from jsonpath_rw import jsonpath, parse

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
        ans = input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def template_exists(template_id):
    result = db[TEMPLATES_COLLECTION].find_one({"@id": template_id})
    if result is not None:
        return True
    else:
        return False

def remove_instance(instance_id):
    print('Removing instance: ' + instance_id)
    db[INSTANCES_COLLECTION].remove({"@id": instance_id})

### end of FUNCTION definitions ###

# Constants
VERSION = '2_23_2017b'
DB_NAME = 'cedar'
UPDATED_DB_NAME = DB_NAME + '-updated-' + VERSION
OLD_DB_NAME = DB_NAME + '-old-' + VERSION
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
print(' --------------------------------------------------')
print('| CEDAR Orphan Instances Cleaner v.' + VERSION + ' |')
print(' --------------------------------------------------')
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

    # Count existing instances
    print('\nNumber of instances: ' + str(db[INSTANCES_COLLECTION].find().count()))

    orphan_instances_ids = []
    for instance in db[INSTANCES_COLLECTION].find():
        instance_id = instance['@id']
        instance_id = instance['@id']
        if 'schema:isBasedOn' in instance:
            template_id = instance['schema:isBasedOn']
            if not template_exists(template_id):
                orphan_instances_ids.append(instance_id)
        else:
            print('schema:isBasedOn is missing for instance: ' + instance_id)
            orphan_instances_ids.append(instance_id)
        
    print('\nList of orphan instances:')
    if len(orphan_instances_ids) == 0:
        print('No orphan instances found!')
    else:
        for oi_id in orphan_instances_ids:
            print(oi_id)
     
    if len(orphan_instances_ids) > 0:
        choice = confirm('\nDo you want to remove these instances from the database?', False)
        if choice is True:
            for oi_id in orphan_instances_ids:
                remove_instance(oi_id)

    print('\nChanges done on the \'' + UPDATED_DB_NAME + '\' database.')

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












