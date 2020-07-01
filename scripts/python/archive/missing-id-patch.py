import jsonpatch
import uuid
import re
import json
import argparse
import os
from python.cedar import print_progressbar
from pymongo import MongoClient


cedar_instance_collection = "template-instances"

mongodb_conn = "mongodb://" + os.environ['CEDAR_MONGO_ROOT_USER_NAME'] + ":" + os.environ['CEDAR_MONGO_ROOT_USER_PASSWORD'] + "@localhost:27017/admin"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-mongodb",
                        required=False,
                        metavar="DBNAME",
                        help="set the MongoDB database where resources are located")
    parser.add_argument("--error-log",
                        required=False,
                        metavar="FILENAME",
                        help="an input file containing the error details")
    args = parser.parse_args()
    input_mongodb = args.input_mongodb
    error_log = args.error_log

    mongodb_client = setup_mongodb_client(mongodb_conn)
    source_database = setup_source_database(mongodb_client, input_mongodb)
    patch_missing_field_in_instances(error_log, source_database)


def patch_missing_field_in_instances(error_log, source_database):
    with open(error_log) as f:
        messages = json.load(f)
        total_messages = len(messages)
        counter = 0
        for key, value in messages.items():
            print_progressbar("Processing...", counter, total_messages, message="Patching")
            instance_ids = get_invalid_instances(value)
            error_path = find_error_path(key)
            if error_path:
                for instance_id in instance_ids:
                    instance = read_from_mongodb(source_database, cedar_instance_collection, instance_id)
                    json_patch = jsonpatch.JsonPatch([{
                        "op": "add",
                        "value": {
                            "@id": "https://repo.staging.metadatacenter.org/template-element-instances/" + str(uuid.uuid4())
                        },
                        "path": error_path
                    }])
                    patched_instance = json_patch.apply(instance)
                    write_to_mongodb(source_database, cedar_instance_collection, patched_instance)
            counter = counter + 1


def get_invalid_instances(value):
    return value


def find_error_path(message):
    pattern = "object has missing required properties \(\['@id'\]\) at (.+)$"
    s = re.search(pattern, message)
    if s:
        return s.group(1)
    else:
        return None


def setup_mongodb_client(conn):
    if conn is None:
        return None
    return MongoClient(conn)


def setup_source_database(mongodb_client, source_db_name):
    if mongodb_client is None or source_db_name is None:
        return None
    db_names = mongodb_client.database_names()
    if source_db_name not in db_names:
        print("ERROR: Input MongoDB database not found: " + source_db_name)
        exit(0)
    return mongodb_client[source_db_name]


def read_from_mongodb(database, collection_name, resource_id):
    return database[collection_name].find_one({'@id': resource_id})


def write_to_mongodb(database, collection_name, resource):
    database[collection_name].replace_one({'@id': resource['@id']}, resource)


if __name__ == "__main__":
    main()
