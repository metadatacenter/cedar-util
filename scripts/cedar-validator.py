import argparse
import requests
from pymongo import MongoClient
from cedar.utils import validator, get_server_address, to_json_string


server_address = None
cedar_api_key = None
report = {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server",
                        choices=['local', 'staging', 'production'],
                        default="staging",
                        help="the type of CEDAR server")
    parser.add_argument("-t", "--type",
                        choices=['template', 'element', 'field', 'instance'],
                        default="template",
                        help="the type of CEDAR resource")
    parser.add_argument("--lookup",
                        required=False,
                        metavar="FILENAME",
                        help="an input file containing a list of resource identifiers to validate")
    parser.add_argument("--limit",
                        required=False,
                        type=int,
                        help="the maximum number of resources to validate")
    parser.add_argument("--validation-apikey",
                        required=False,
                        metavar="CEDAR-API-KEY",
                        help="the API key used to access the CEDAR validation service")
    parser.add_argument("--mongodb-connection",
                        required=False,
                        metavar="DBCONN",
                        help="set the MongoDB admin connection URI to perform administration operations")
    parser.add_argument("--input-mongodb",
                        required=False,
                        default="cedar",
                        metavar="DBNAME",
                        help="set the MongoDB database name to get the resources to validate")
    args = parser.parse_args()
    resource_type = args.type
    lookup_file = args.lookup
    limit = args.limit

    global server_address, cedar_api_key
    server_address = get_server_address(args.server)
    cedar_api_key = args.validation_apikey
    mongodb_conn = args.mongodb_connection
    source_db_name = args.input_mongodb

    mongodb_client = setup_mongodb_client(mongodb_conn)
    source_database = setup_source_database(mongodb_client, source_db_name)

    if resource_type == 'template':
        template_ids = get_template_ids(lookup_file, source_database, limit)
        validate_template(template_ids, source_database)
    elif resource_type == 'element':
        element_ids = get_element_ids(lookup_file, source_database, limit)
        validate_element(element_ids, source_database)
    elif resource_type == 'field':
        pass
    elif resource_type == 'instance':
        instance_ids = get_instance_ids(lookup_file, source_database, limit)
        validate_instance(instance_ids, source_database)

    show_report()


def validate_template(template_ids, source_database):
    total_templates = len(template_ids)
    for counter, template_id in enumerate(template_ids, start=1):
        print_progressbar(template_id, counter, total_templates)
        try:
            template = get_template_from_mongodb(source_database, template_id)
            is_valid, validation_message = validator.validate_template(server_address, cedar_api_key, template)
            reporting(template_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            exit(error)


def validate_element(element_ids, source_database):
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        print_progressbar(element_id, counter, total_elements)
        try:
            element = get_element_from_mongodb(source_database, element_id)
            is_valid, validation_message = validator.validate_element(server_address, cedar_api_key, element)
            reporting(element_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            exit(error)


def validate_instance(instance_ids, source_database):
    total_instances = len(instance_ids)
    for counter, instance_id in enumerate(instance_ids, start=1):
        print_progressbar(instance_id, counter, total_instances)
        try:
            instance = get_instance_from_mongodb(source_database, instance_id)
            is_valid, validation_message = validator.validate_instance(server_address, cedar_api_key, instance)
            reporting(instance_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            exit(error)


def get_template_ids(lookup_file, source_database, limit):
    template_ids = []
    if lookup_file is not None:
        template_ids.extend(get_ids_from_file(lookup_file))
    else:
        if limit:
            template_ids = source_database['templates'].distinct("@id").limit(limit)
        else:
            template_ids = source_database['templates'].distinct("@id")
    return template_ids


def get_element_ids(lookup_file, source_database, limit):
    element_ids = []
    if lookup_file is not None:
        element_ids.extend(get_ids_from_file(lookup_file))
    else:
        if limit:
            element_ids = source_database['template-elements'].distinct("@id").limit(limit)
        else:
            element_ids = source_database['template-elements'].distinct("@id")
    return element_ids


def get_instance_ids(lookup_file, source_database, limit):
    instance_ids = []
    if lookup_file is not None:
        instance_ids.extend(get_ids_from_file(lookup_file))
    else:
        if limit:
            instance_ids = source_database['template-instances'].distinct("@id").limit(limit)
        else:
            instance_ids = source_database['template-instances'].distinct("@id")
    return instance_ids


def get_ids_from_file(filename):
    with open(filename) as infile:
        resource_ids = infile.readlines()
        return [id.strip() for id in resource_ids]


def get_template_from_mongodb(source_database, template_id):
    template = source_database['templates'].find_one({'@id': template_id})
    return post_read(template)


def get_element_from_mongodb(source_database, element_id):
    element = source_database['template-elements'].find_one({'@id': element_id})
    return post_read(element)


def get_instance_from_mongodb(source_database, instance_id):
    instance = source_database['template-instances'].find_one({'@id': instance_id})
    return post_read(instance)


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


if __name__ == "__main__":
    main()
