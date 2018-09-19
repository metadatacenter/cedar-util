import argparse
import os
import json
import requests
from pymongo import MongoClient
from cedar.utils import validator, getter, to_json_string


cedar_template_collection = "templates"
cedar_element_collection = "template-elements"
cedar_field_collection = "template-fields"
cedar_instance_collection = "template-instances"

cedar_server_address = "https://resource." + os.environ['CEDAR_HOST']
cedar_api_key = "apiKey " + os.environ['CEDAR_ADMIN_USER_API_KEY']
mongodb_conn = "mongodb://" + os.environ['CEDAR_MONGO_ROOT_USER_NAME'] + ":" + os.environ['CEDAR_MONGO_ROOT_USER_PASSWORD'] + "@localhost:27017/admin"
report = {}
error_messages = []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type",
                        choices=['template', 'element', 'field', 'instance'],
                        default="template",
                        help="the type of CEDAR resource")
    parser.add_argument("--input-list",
                        required=False,
                        metavar="FILENAME",
                        help="an input file containing a list of resource identifiers to validate")
    parser.add_argument("--input-json",
                        required=False,
                        metavar="FILENAME",
                        help="an input file containing the JSON document to validate")
    parser.add_argument("--input-mongodb",
                        required=False,
                        metavar="DBNAME",
                        help="the name of MongoDB database where resources are located")
    parser.add_argument("--limit",
                        required=False,
                        type=int,
                        help="the maximum number of resources to validate (useful when --input-mongodb is used)")
    args = parser.parse_args()
    resource_type = args.type
    input_file = args.input_json
    input_list = args.input_list
    input_mongodb = args.input_mongodb
    limit = args.limit

    if input_file is not None:
        if resource_type == 'template':
            template = read_json(input_file)
            validate_template_from_json(template)
        elif resource_type == 'element':
            element = read_json(input_file)
            validate_element_from_json(element)
        elif resource_type == 'field':
            field = read_json(input_file)
            validate_field_from_json(field)
        elif resource_type == 'instance':
            instance = read_json(input_file)
            validate_instance_from_json(instance)
    elif input_list is not None:
        if resource_type == 'template':
            template_ids = read_list(input_list)
            validate_template_from_list(template_ids)
        elif resource_type == 'element':
            element_ids = read_list(input_list)
            validate_element_from_list(element_ids)
        elif resource_type == 'field':
            field_ids = read_list(input_list)
            validate_field_from_list(field_ids)
        elif resource_type == 'instance':
            instance_ids = read_list(input_list)
            validate_instance_from_list(instance_ids)
    elif input_mongodb is not None:
        mongodb_client = setup_mongodb_client(mongodb_conn)
        source_database = setup_source_database(mongodb_client, input_mongodb)
        if resource_type == 'template':
            template_ids = get_resource_ids(source_database, cedar_template_collection, limit)
            validate_template_from_mongodb(template_ids, source_database)
        elif resource_type == 'element':
            element_ids = get_resource_ids(source_database, cedar_element_collection, limit)
            validate_element_from_mongodb(element_ids, source_database)
        elif resource_type == 'field':
            field_ids = get_resource_ids(source_database, cedar_field_collection, limit)
            validate_field_from_mongodb(field_ids, source_database)
        elif resource_type == 'instance':
            instance_ids = get_resource_ids(source_database, cedar_instance_collection, limit)
            validate_instance_from_mongodb(instance_ids, source_database)

    show_report()


def validate_template_from_json(template):
    try:
        template_id = template["@id"]
        is_valid, validation_message = validator.validate_template(cedar_server_address, cedar_api_key, template)
        reporting(template_id, is_valid, validation_message)
    except requests.exceptions.HTTPError as error:
        error_obj = json.loads(error.response.text)
        error_messages.append(error_obj["message"])


def validate_template_from_list(template_ids):
    total_templates = len(template_ids)
    for counter, template_id in enumerate(template_ids, start=1):
        print_progressbar(template_id, counter, total_templates)
        try:
            template = get_template_from_server(cedar_server_address, cedar_api_key, template_id)
            is_valid, validation_message = validator.validate_template(cedar_server_address, cedar_api_key, template)
            reporting(template_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            error_obj = json.loads(error.response.text)
            error_messages.append(error_obj["message"])
            pass


def validate_template_from_mongodb(template_ids, source_database):
    total_templates = len(template_ids)
    for counter, template_id in enumerate(template_ids, start=1):
        print_progressbar(template_id, counter, total_templates)
        try:
            template = read_from_mongodb(source_database, cedar_template_collection, template_id)
            is_valid, validation_message = validator.validate_template(cedar_server_address, cedar_api_key, template)
            reporting(template_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            error_obj = json.loads(error.response.text)
            error_messages.append(error_obj["message"])
            pass


def validate_element_from_json(element):
    try:
        element_id = element["@id"]
        is_valid, validation_message = validator.validate_element(cedar_server_address, cedar_api_key, element)
        reporting(element_id, is_valid, validation_message)
    except requests.exceptions.HTTPError as error:
        error_obj = json.loads(error.response.text)
        error_messages.append(error_obj["message"])


def validate_element_from_list(element_ids):
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        print_progressbar(element_id, counter, total_elements)
        try:
            element = get_element_from_server(cedar_server_address, cedar_api_key, element_id)
            is_valid, validation_message = validator.validate_element(cedar_server_address, cedar_api_key, element)
            reporting(element_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            error_obj = json.loads(error.response.text)
            error_messages.append(error_obj["message"])
            pass


def validate_element_from_mongodb(element_ids, source_database):
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        print_progressbar(element_id, counter, total_elements)
        try:
            element = read_from_mongodb(source_database, cedar_element_collection, element_id)
            is_valid, validation_message = validator.validate_element(cedar_server_address, cedar_api_key, element)
            reporting(element_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            error_obj = json.loads(error.response.text)
            error_messages.append(error_obj["message"])
            pass


def validate_field_from_json(field):
    try:
        field_id = field["@id"]
        is_valid, validation_message = validator.validate_field(cedar_server_address, cedar_api_key, field)
        reporting(field_id, is_valid, validation_message)
    except requests.exceptions.HTTPError as error:
        error_obj = json.loads(error.response.text)
        error_messages.append(error_obj["message"])


def validate_field_from_list(field_ids):
    total_fields = len(field_ids)
    for counter, field_id in enumerate(field_ids, start=1):
        print_progressbar(field_id, counter, total_fields)
        try:
            field = get_field_from_server(cedar_server_address, cedar_api_key, field_id)
            is_valid, validation_message = validator.validate_field(cedar_server_address, cedar_api_key, field)
            reporting(field_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            error_obj = json.loads(error.response.text)
            error_messages.append(error_obj["message"])
            pass


def validate_field_from_mongodb(field_ids, source_database):
    total_fields = len(field_ids)
    for counter, field_id in enumerate(field_ids, start=1):
        print_progressbar(field_id, counter, total_fields)
        try:
            field = read_from_mongodb(source_database, cedar_field_collection, field_id)
            is_valid, validation_message = validator.validate_field(cedar_server_address, cedar_api_key, field)
            reporting(field_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            error_obj = json.loads(error.response.text)
            error_messages.append(error_obj["message"])
            pass


def validate_instance_from_json(instance):
    try:
        instance_id = instance["@id"]
        is_valid, validation_message = validator.validate_instance(cedar_server_address, cedar_api_key, instance)
        reporting(instance_id, is_valid, validation_message)
    except requests.exceptions.HTTPError as error:
        error_obj = json.loads(error.response.text)
        error_messages.append(error_obj["message"])


def validate_instance_from_list(instance_ids):
    total_instances = len(instance_ids)
    for counter, instance_id in enumerate(instance_ids, start=1):
        print_progressbar(instance_id, counter, total_instances)
        try:
            instance = get_instance_from_server(cedar_server_address, cedar_api_key, instance_id)
            is_valid, validation_message = validator.validate_instance(cedar_server_address, cedar_api_key, instance)
            reporting(instance_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            error_obj = json.loads(error.response.text)
            error_messages.append(error_obj["message"])
            pass


def validate_instance_from_mongodb(instance_ids, source_database):
    total_instances = len(instance_ids)
    for counter, instance_id in enumerate(instance_ids, start=1):
        print_progressbar(instance_id, counter, total_instances)
        try:
            instance = read_from_mongodb(source_database, cedar_instance_collection, instance_id)
            is_valid, validation_message = validator.validate_instance(cedar_server_address, cedar_api_key, instance)
            reporting(instance_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            error_obj = json.loads(error.response.text)
            error_messages.append(error_obj["message"])
            pass


def get_resource_ids(database, collection_name, limit):
    resource_ids = []
    if limit:
        found_ids = database[collection_name].distinct("@id").limit(limit)
        resource_ids.extend(found_ids)
    else:
        found_ids = database[collection_name].distinct("@id")
        resource_ids.extend(found_ids)
    filtered_ids = filter(lambda x: x is not None, resource_ids)
    return list(filtered_ids)


def read_list(filename):
    with open(filename) as infile:
        resource_ids = infile.readlines()
        return [id.strip() for id in resource_ids]


def read_json(filename):
    with open(filename) as infile:
        content = json.load(infile)
        return content


def get_template_from_server(server_address, api_key, template_id):
    return getter.get_template(server_address, api_key, template_id)


def get_element_from_server(server_address, api_key, element_id):
    return getter.get_element(server_address, api_key, element_id)


def get_field_from_server(server_address, api_key, field_id):
    return getter.get_field(server_address, api_key, field_id)


def get_instance_from_server(server_address, api_key, instance_id):
    return getter.get_instance(server_address, api_key, instance_id)


def read_from_mongodb(database, collection_name, resource_id):
    resource = database[collection_name].find_one({'@id': resource_id})
    return post_read(resource)


def post_read(resource):
    new = {}
    for k, v in resource.items():
        if k == '_id':
            continue
        if isinstance(v, dict):
            v = post_read(v)
        new[k.replace('_$schema', '$schema')] = v
    return new


def setup_mongodb_client(mongodb_conn):
    if mongodb_conn is None:
        return None
    return MongoClient(mongodb_conn)


def setup_source_database(mongodb_client, source_db_name):
    if mongodb_client is None or source_db_name is None:
        return None

    db_names = mongodb_client.database_names()
    if source_db_name not in db_names:
        print(" ERROR    | Input MongoDB database not found: " + source_db_name)
        exit(0)

    return mongodb_client[source_db_name]


def reporting(resource_id, is_valid, validation_message):
    if not is_valid:
        for error_details in validation_message["errors"]:
            error_message = error_details['message'] + " at " + error_details['location']
            report.setdefault(error_message,[]).append(resource_id)


def print_progressbar(resource_id, counter, total_count):
    resource_hash = extract_resource_hash(resource_id)
    percent = 100 * (counter / total_count)
    filled_length = int(percent)
    bar = "#" * filled_length + '-' * (100 - filled_length)
    print("\rValidating (%d/%d): |%s| %d%% Complete [%s]" % (counter, total_count, bar, percent, resource_hash), end='\r')


def extract_resource_hash(resource_id):
    return resource_id[resource_id.rfind('/')+1:]


def show_report():
    report_size = len(report)
    message = "No error was found."
    if report_size > 0:
        message = "Found " + str(report_size) + " validation error(s)."
        message += "\n"
        message += "Details: " + to_json_string(dict(report))
    print("\n" + message)
    print()
    error_size = len(error_messages)
    if error_size > 0:
        print()
        print("Found errors:")
        for msg in error_messages:
            print("- " + msg)
        print()


if __name__ == "__main__":
    main()
