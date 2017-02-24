#!/usr/bin/python

# Created: 2016-Aug-16
# Last update: 2017-Feb-22
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

def template_exists(template_id):
    result = db[TEMPLATES_COLLECTION].find_one({"@id": template_id})
    if result is not None:
        return True
    else:
        return False

### end of FUNCTION definitions ###

# Constants
VERSION = '2_23_2017'
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

    orphan_instances = []
    for instance in db[INSTANCES_COLLECTION].find():
        instance_id = instance['@id']
        instance_id = instance['@id']
        template_id = instance['schema:isBasedOn']
        if not template_exists(template_id):
            orphan_instances.append(instance_id)

    print('\nList of orphan instances:')
    if len(orphan_instances) == 0:
        print('No orphan instances found!')
    else:
        for oi in orphan_instances:
            print(oi)
     
    # # Update resources
    # resources_number = {}
    # for collection in RESOURCE_COLLECTIONS:
    #     resources = db[collection].find()
    #     resources_number[collection] = resources.count()
    #     j=0
    #     for resource in resources:
    #         j=j+1
    #         update_model(resource, j, resources_number[collection])
    #         # Replace document in the DB with the updated version
    #         db[collection].replace_one({'_id':resource['_id']}, resource)

    # print('\nUpdate finished.')
    # print('\nThe updated resources have been stored into the \'' + UPDATED_DB_NAME + '\' database.')

    # choice = confirm('Do you want to rename the DBs as follows?\n 1)\'' + DB_NAME + '\' to \'' + OLD_DB_NAME + '\'\n 2)\'' + UPDATED_DB_NAME + '\' to \'' + DB_NAME + '\'\n', False)

    # if choice is True:
    #     # rename DB_NAME to OLD_DB_NAME
    #     print('Renaming \'' + DB_NAME + '\' to \'' + OLD_DB_NAME + '\'...')
    #     client.drop_database(OLD_DB_NAME)
    #     client.admin.command('copydb', fromdb=DB_NAME, todb=OLD_DB_NAME)
    #     client.drop_database(DB_NAME)
    #     # rename UPDATED_DB_NAME to DB_NAME
    #     print('Renaming \'' + UPDATED_DB_NAME + '\' to \'' + DB_NAME + '\'...')
    #     client.admin.command('copydb', fromdb=UPDATED_DB_NAME, todb=DB_NAME)
    #     client.drop_database(UPDATED_DB_NAME)
    #     print('Finished renaming the DBs')















