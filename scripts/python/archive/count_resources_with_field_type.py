#!/usr/bin/python

# Created: 2017-Feb-23
# Last update: 2017-Feb-23
# count_resources_with_field_type.py: Utility to count the number of CEDAR resources (elements, templates, and instances) in a MongoDB database that make use of the field type feature.

import json
import sys
from pymongo import MongoClient
from pprint import pprint
from jsonpath_rw import jsonpath, parse

### FUNCTION definitions ###
def __getattr__(self, name):
        return self[name]
### end of FUNCTION definitions ###

# Constants
DB_NAME = 'cedar'
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
BIOPORTAL_PREFIX = 'http://data.bioontology.org'

### Main program ###
print(' -----------------------------')
print('| CEDAR Field Type Counter    |')
print(' -----------------------------')

client = MongoClient()
dbnames = client.database_names()

if DB_NAME not in dbnames:
    raise Exception('Database \'' + DB_NAME + '\' does not exist')

db = client[DB_NAME]

# Count existing resources
print('\nNumber of resources:')
for collection in RESOURCE_COLLECTIONS:
    print('   ' + collection + ': ' + str(db[collection].find().count()))
print

print('\nCounting...\n')

count_resources = {}
count_field_types = {}
for collection in RESOURCE_COLLECTIONS:
    for resource in db[collection].find():
        # Get resource type
        if '@type' in resource:
            resource_type = resource['@type'].rsplit('/', 1)[-1]
        else:
            resource_type = INSTANCE_TYPE

        if resource_type not in count_resources:
            count_resources[resource_type] = 0
        if resource_type not in count_field_types:
            count_field_types[resource_type] = 0

        count = 0
        if resource_type == TEMPLATE_TYPE or resource_type == ELEMENT_TYPE:
            for match in parse('$..items.enum').find(resource):
                enum_value = match.value[0]
                if enum_value.startswith(BIOPORTAL_PREFIX):
                    count = count + 1
        elif resource_type == INSTANCE_TYPE:
            for match in parse('$..@type').find(resource):
                if type(match.value) is list:
		    for v in match.value:
		        if v.startswith(BIOPORTAL_PREFIX):
                    	    count = count + 1
                elif match.value.startswith(BIOPORTAL_PREFIX):
		    count = count + 1

        if count > 0:
            count_resources[resource_type] = count_resources[resource_type] + 1
            count_field_types[resource_type] = count_field_types[resource_type] + count

print('Results:')
print('   Number of resources that are using the field type:')
for rt in count_resources:
    print('      ' + rt + 's: ' + str(count_resources[rt]))

print('\n   Number field types used:')
for rt in count_field_types:
    print('      In ' + rt + 's: ' + str(count_field_types[rt]))



       
        









