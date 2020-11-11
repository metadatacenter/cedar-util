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
    parser.add_argument("--input-list",
                        required=False,
                        metavar="FILENAME",
                        help="an input file containing a list of resource identifiers to validate")
    args = parser.parse_args()
    input_mongodb = args.input_mongodb
    input_list = args.input_list

    mongodb_client = setup_mongodb_client(mongodb_conn)
    source_database = setup_source_database(mongodb_client, input_mongodb)
    instance_ids = read_list(input_list)
    patch_skos_in_instances(instance_ids, source_database)


def patch_skos_in_instances(instance_ids, database):
    total_instances = len(instance_ids)
    for counter, instance_id in enumerate(instance_ids, start=1):
        print_progressbar(instance_id, counter, total_instances, message="Patching")
        instance = read_from_mongodb(database, cedar_instance_collection, instance_id)
        instance["@context"]["skos"] = "http://www.w3.org/2004/02/skos/core#"
        instance["@context"]["skos:notation"] = { "@type": "xsd:string" }
        write_to_mongodb(database, cedar_instance_collection, instance)


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


def read_list(filename):
    with open(filename) as infile:
        resource_ids = infile.readlines()
        return [id.strip() for id in resource_ids]


def read_from_mongodb(database, collection_name, resource_id):
    return database[collection_name].find_one({'@id': resource_id})


def write_to_mongodb(database, collection_name, resource):
    database[collection_name].replace_one({'@id': resource['@id']}, resource)


if __name__ == "__main__":
    main()
