#!/usr/local/bin/python3

# Script to generate a report with the number of resources generated per month

from pymongo import MongoClient
from os import environ
import json

# FUNCTION definitions #
def __getattr__(self, name):
    return self[name]
# end of FUNCTION definitions #

# Constants
DB_NAME = 'cedar'
TEMPLATES_COLLECTION = 'templates'
ELEMENTS_COLLECTION = 'template-elements'
INSTANCES_COLLECTION = 'template-instances'
TEMPLATE_TYPE = 'Template'
ELEMENT_TYPE = 'TemplateElement'
FIELD_TYPE = 'TemplateField'
INSTANCE_TYPE = 'TemplateInstance'
RESOURCE_COLLECTIONS = [TEMPLATES_COLLECTION, ELEMENTS_COLLECTION, INSTANCES_COLLECTION]

# Values extracted from CEDAR environment variables
MONGO_HOST=environ.get('CEDAR_MONGO_HOST')
MONGO_PORT=environ.get('CEDAR_MONGO_PORT')
MONGO_ROOT_USER_NAME=environ.get('CEDAR_MONGO_ROOT_USER_NAME')
MONGO_ROOT_USER_PASSWORD=environ.get('CEDAR_MONGO_ROOT_USER_PASSWORD')

CREATED_ON_FIELD = 'pav:createdOn'

def get_mongo_client():
    connection_string='mongodb://%s:%s@%s:%s' % (MONGO_ROOT_USER_NAME, MONGO_ROOT_USER_PASSWORD, MONGO_HOST, MONGO_PORT)
    return MongoClient(connection_string)

# Main program #

print(' ------------------------------')
print('| CEDAR resources/month report |')
print(' ------------------------------')

client = get_mongo_client()
dbnames = client.database_names()

if DB_NAME not in dbnames:
    raise Exception('Database \'' + DB_NAME + '\' does not exist')

db = client[DB_NAME]

print('\nGenerating report...\n')

print('\nTotal number of resources:\n')
for collection in RESOURCE_COLLECTIONS:
    print('  - ' + collection + ': ' + str(db[collection].find().count()))

print('\nNo. resources created per month:\n')

created_on_summary = {
    TEMPLATES_COLLECTION: {},
    ELEMENTS_COLLECTION: {},
    INSTANCES_COLLECTION: {}
}

for collection in RESOURCE_COLLECTIONS:
    for resource in db[collection].find():
        if CREATED_ON_FIELD in resource:
            created_on = resource[CREATED_ON_FIELD]
            date = str(created_on[0:7])
            if date not in created_on_summary[collection]:
                created_on_summary[collection][date] = 0
            else:
                created_on_summary[collection][date] = created_on_summary[collection][date] + 1

print(json.dumps(created_on_summary, sort_keys=True, indent=4, separators=(',', ': ')))
