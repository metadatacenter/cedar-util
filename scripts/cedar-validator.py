import argparse
import requests
from cedar.utils import getter, searcher, validator, get_server_address, to_json_string


server_address = None
cedar_api_key = None
report = {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server",
                        choices=['local', 'staging', 'production'],
                        default="staging",
                        help="The type of CEDAR server")
    parser.add_argument("-t", "--type",
                        choices=['template', 'element', 'field', 'instance'],
                        default="template",
                        help="The type of CEDAR resource")
    parser.add_argument("--lookup",
                        required=False,
                        metavar="FILENAME",
                        help="An input file containing a list of resource identifiers to patch")
    parser.add_argument("--limit",
                        required=False,
                        type=int,
                        help="The maximum number of resources to validate")
    parser.add_argument("apikey", metavar="CEDAR-API-KEY",
                        help="The API key used to query the CEDAR resource server")
    args = parser.parse_args()
    resource_type = args.type
    lookup_file = args.lookup
    limit = args.limit

    global server_address, cedar_api_key
    server_address = get_server_address(args.server)
    cedar_api_key = args.apikey

    if resource_type == 'template':
        template_ids = get_template_ids(lookup_file, limit)
        validate_template(template_ids)
    elif resource_type == 'element':
        element_ids = get_element_ids(lookup_file, limit)
        validate_element(element_ids)
    elif resource_type == 'field':
        pass
    elif resource_type == 'instance':
        instance_ids = get_instance_ids(lookup_file, limit)
        validate_instance(lookup_file, limit)

    show_report()


def validate_template(template_ids):
    total_templates = len(template_ids)
    for counter, template_id in enumerate(template_ids, start=1):
        print_progressbar(template_id, counter, total_templates)
        try:
            template = get_template(template_id)
            is_valid, validation_message = validator.validate_template(server_address, cedar_api_key, template)
            reporting(template_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            exit(error)


def validate_element(element_ids):
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        print_progressbar(element_id, counter, total_elements)
        try:
            element = get_element(element_id)
            is_valid, validation_message = validator.validate_element(server_address, cedar_api_key, element)
            reporting(element_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            exit(error)


def validate_instance(instance_ids):
    total_instances = len(instance_ids)
    for counter, instance_id in enumerate(instance_ids, start=1):
        print_progressbar(instance_id, counter, total_instances)
        try:
            instance = get_instance(instance_id)
            is_valid, validation_message = validator.validate_instance(server_address, cedar_api_key, instance)
            reporting(instance_id, is_valid, validation_message)
        except requests.exceptions.HTTPError as error:
            exit(error)


def get_template_ids(lookup_file, limit):
    template_ids = []
    if lookup_file is not None:
        template_ids.extend(get_ids_from_file(lookup_file))
    else:
        template_ids = searcher.search_templates(server_address, cedar_api_key, max_count=limit)
    return template_ids


def get_element_ids(lookup_file, limit):
    element_ids = []
    if lookup_file is not None:
        element_ids.extend(get_ids_from_file(lookup_file))
    else:
        element_ids = searcher.search_elements(server_address, cedar_api_key, max_count=limit)
    return element_ids


def get_instance_ids(lookup_file, limit):
    instance_ids = []
    if lookup_file is not None:
        instance_ids.extend(get_ids_from_file(lookup_file))
    else:
        instance_ids = searcher.search_instances(server_address, cedar_api_key, max_count=limit)
    return instance_ids


def get_ids_from_file(filename):
    with open(filename) as infile:
        resource_ids = infile.readlines()
        return [id.strip() for id in resource_ids]


def get_template(template_id):
    return getter.get_template(server_address, cedar_api_key, template_id)


def get_element(element_id):
    return getter.get_element(server_address, cedar_api_key, element_id)


def get_instance(instance_id):
    return getter.get_instance(server_address, cedar_api_key, instance_id)


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
