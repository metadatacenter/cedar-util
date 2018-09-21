import argparse
import os
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
                        default="template",
                        help="the type of CEDAR resource")
    parser.add_argument("--input-mongodb",
                        required=False,
                        default="cedar",
                        metavar="DBNAME",
                        help="set the MongoDB database where resources are located")
    parser.add_argument("--version-number",
                        help="the new version number for schema:schemaVersion field")

    args = parser.parse_args()
    resource_type = args.type
    cedar_database = args.input_mongodb
    version_number = args.version_number

    mongodb_client = MongoClient(mongodb_conn)
    database = mongodb_client[cedar_database]
    if resource_type == 'template':
        template_ids = get_resource_ids(database, cedar_template_collection)
        update_template_model_version(template_ids, database, version_number)
    elif resource_type == 'element':
        element_ids = get_resource_ids(database, cedar_element_collection)
        update_element_model_version(element_ids, database, version_number)
    elif resource_type == 'field':
        field_ids = get_resource_ids(database, cedar_field_collection)
        update_field_model_version(field_ids, database, version_number)


def update_template_model_version(template_ids, database, model_version):
    total_templates = len(template_ids)
    for counter, template_id in enumerate(template_ids, start=1):
        print_progressbar(template_id, counter, total_templates)
        template = read_from_mongodb(database, cedar_template_collection, template_id)
        set_model_version(template, model_version)
        write_to_mongodb(database, cedar_template_collection, template)
    print()  # console printing separator


def update_element_model_version(element_ids, database, model_version):
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        print_progressbar(element_id, counter, total_elements)
        element = read_from_mongodb(database, cedar_element_collection, element_id)
        set_model_version(element, model_version)
        write_to_mongodb(database, cedar_element_collection, element)
    print()  # console printing separator


def update_field_model_version(field_ids, database, model_version):
    total_fields = len(field_ids)
    for counter, field_id in enumerate(field_ids, start=1):
        print_progressbar(field_id, counter, total_fields)
        field = read_from_mongodb(database, cedar_field_collection, field_id)
        set_model_version(field, model_version)
        write_to_mongodb(database, cedar_field_collection, field)
    print()  # console printing separator


def set_model_version(resource, model_version):
    if resource is None:
        return
    for k, v in resource.items():
        if isinstance(v, dict):
            set_model_version(v, model_version)
        elif isinstance(v, str):
            if k == "schema:schemaVersion":
                resource[k] = model_version


def get_resource_ids(database, collection_name):
    resource_ids = []
    found_ids = database[collection_name].distinct("@id")
    resource_ids.extend(found_ids)
    filtered_ids = filter(lambda x: x is not None, resource_ids)
    return list(filtered_ids)


def read_from_mongodb(database, collection_name, resource_id):
    return database[collection_name].find_one({'@id': resource_id})


def write_to_mongodb(database, collection_name, resource):
    database[collection_name].replace_one({'@id': resource['@id']}, resource)


def print_progressbar(resource_id, counter, total_count):
    resource_hash = extract_resource_hash(resource_id)
    percent = 100 * (counter / total_count)
    filled_length = int(percent)
    bar = "#" * filled_length + '-' * (100 - filled_length)
    print("Updating (%d/%d): |%s| %d%% Complete [%s]" % (counter, total_count, bar, percent, resource_hash), end='\r')


def extract_resource_hash(resource_id):
    return resource_id[resource_id.rfind('/')+1:]


if __name__ == "__main__":
    main()
