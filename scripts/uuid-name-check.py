import argparse
import os
import re
from cedar.utils import to_json_string
from pymongo import MongoClient


cedar_template_collection = "templates"
cedar_element_collection = "template-elements"
cedar_field_collection = "template-fields"

cedar_server_address = "https://resource." + os.environ['CEDAR_HOST']
cedar_api_key = "apiKey " + os.environ['CEDAR_ADMIN_USER_API_KEY']
mongodb_conn = "mongodb://" + os.environ['CEDAR_MONGO_ROOT_USER_NAME'] + ":" + os.environ['CEDAR_MONGO_ROOT_USER_PASSWORD'] + "@localhost:27017/admin"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type",
                        choices=['template', 'element', 'field'],
                        help="the type of CEDAR resource")
    parser.add_argument("--input-mongodb",
                        required=False,
                        metavar="DBNAME",
                        help="set the MongoDB database where resources are located")

    args = parser.parse_args()
    resource_type = args.type
    cedar_database = args.input_mongodb

    mongodb_client = MongoClient(mongodb_conn)
    database = mongodb_client[cedar_database]
    if resource_type == 'template':
        template_ids = get_resource_ids(database, cedar_template_collection)
        check_uuid_in_templates(template_ids, database)
    elif resource_type == 'element':
        element_ids = get_resource_ids(database, cedar_element_collection)
        check_uuid_in_elements(element_ids, database)
    elif resource_type == 'field':
        field_ids = get_resource_ids(database, cedar_field_collection)
        check_uuid_in_fields(field_ids, database)


def check_uuid_in_templates(template_ids, database):
    report = []
    total_templates = len(template_ids)
    for counter, template_id in enumerate(template_ids, start=1):
        print_progressbar(template_id, counter, total_templates)
        template = read_from_mongodb(database, cedar_template_collection, template_id)
        report_item = perform_check(template)
        if report_item["locations"]:
            report.append(report_item)
    show(report)


def check_uuid_in_elements(element_ids, database):
    report = []
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        print_progressbar(element_id, counter, total_elements)
        element = read_from_mongodb(database, cedar_element_collection, element_id)
        report_item = perform_check(element)
        if report_item["locations"]:
            report.append(report_item)
    show(report)


def check_uuid_in_fields(field_ids, database):
    report = []
    total_fields = len(field_ids)
    for counter, field_id in enumerate(field_ids, start=1):
        print_progressbar(field_id, counter, total_fields)
        field = read_from_mongodb(database, cedar_field_collection, field_id)
        report_item = perform_check(field)
        if report_item["locations"]:
            report.append(report_item)
    show(report)


def perform_check(obj):
    report_item = {
        "id": obj["@id"],
        "locations": []
    }
    check_recursively(obj, "", report_item["locations"])
    return report_item


def check_recursively(obj, pointer, error_locations):
    if obj is None:
        return
    for k, v in obj.items():
        if valid_uuid(k):
            error_locations.append(pointer + "/" + k)
        if isinstance(v, dict):
            check_recursively(v, pointer + "/" + k, error_locations)


def get_resource_ids(database, collection_name):
    resource_ids = []
    found_ids = database[collection_name].distinct("@id")
    resource_ids.extend(found_ids)
    filtered_ids = filter(lambda x: x is not None, resource_ids)
    return list(filtered_ids)


def read_from_mongodb(database, collection_name, resource_id):
    return database[collection_name].find_one({'@id': resource_id})


def print_progressbar(resource_id, counter, total_count):
    resource_hash = extract_resource_hash(resource_id)
    percent = 100 * (counter / total_count)
    filled_length = int(percent)
    bar = "#" * filled_length + '-' * (100 - filled_length)
    print("Checking (%d/%d): |%s| %d%% Complete [%s]" % (counter, total_count, bar, percent, resource_hash), end='\r')


def extract_resource_hash(resource_id):
    return resource_id[resource_id.rfind('/')+1:]


def valid_uuid(uuid):
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    match = regex.match(uuid)
    return bool(match)


def show(report):
    report_size = len(report)
    message = "No UUID field names were found."
    if report_size > 0:
        if report_size == 1:
            message = "Found 1 resource contains UUID field names."
        else:
            message = "Found " + str(report_size) + " resources contain UUID field names."
        message += "\n"
        message += "Details: " + to_json_string(report)
    print("\n" + message)
    print()


if __name__ == "__main__":
    main()
