import argparse
import requests
from cedar.utils import getter, searcher, validator, get_server_address, to_json_string
from collections import defaultdict


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
    parser.add_argument("--limit",
                        required=False,
                        type=int,
                        help="The maximum number of resources to validate")
    parser.add_argument("apikey", metavar="apiKey",
                        help="The API key used to query the CEDAR resource server")
    args = parser.parse_args()
    server_address = get_server_address(args.server)
    type = args.type
    limit = args.limit
    api_key = args.apikey

    report = create_empty_report()

    try:
        if type == 'template':
            validate_template(api_key, server_address, limit, report)
        elif type == 'element':
            validate_element(api_key, server_address, limit, report)
        elif type == 'field':
            pass
        elif type == 'instance':
            validate_instance(api_key, server_address, limit, report)
    except requests.exceptions.HTTPError as error:
        exit(error)

    show(report)


def validate_template(api_key, server_address, limit, report):
    template_ids = get_template_ids(api_key, server_address, limit)
    total_templates = len(template_ids)
    for index, template_id in enumerate(template_ids, start=1):
        template = get_template(api_key, server_address, template_id)
        is_valid, validation_message = validator.validate_template(server_address, api_key, template)
        consume(report, template_id, is_valid, validation_message, iteration=index, total_count=total_templates)


def validate_element(api_key, server_address, limit, report):
    element_ids = get_element_ids(api_key, server_address, limit)
    total_elements = len(element_ids)
    for index, element_id in enumerate(element_ids, start=1):
        element = get_element(api_key, server_address, element_id)
        is_valid, validation_message = validator.validate_element(server_address, api_key, element)
        consume(report, element_id, is_valid, validation_message, iteration=index, total_count=total_elements)


def validate_instance(api_key, server_address, limit, report):
    instance_ids = get_instance_ids(api_key, server_address, limit)
    total_instances = len(instance_ids)
    for index, instance_id in enumerate(instance_ids, start=1):
        instance = get_instance(api_key, server_address, instance_id)
        is_valid, validation_message = validator.validate_instance(server_address, api_key, instance)
        consume(report, instance_id, is_valid, validation_message, iteration=index, total_count=total_instances)


def get_element_ids(api_key, server_address, limit):
    return searcher.search_elements(server_address, api_key, max_count=limit)


def get_template_ids(api_key, server_address, limit):
    return searcher.get_templates(server_address, api_key, max_count=limit)


def get_instance_ids(api_key, server_address, limit):
    return searcher.search_instances(server_address, api_key, max_count=limit)


def get_template(api_key, server_address, template_id):
    return getter.get_template(server_address, api_key, template_id)


def get_element(api_key, server_address, element_id):
    return getter.get_element(server_address, api_key, element_id)


def get_instance(api_key, server_address, instance_id):
    return getter.get_instance(server_address, api_key, instance_id)


def create_empty_report():
    return defaultdict(list)


def consume(report, resource_id, is_valid, validation_message, **kwargs):
    if not is_valid:
        for error_details in validation_message["errors"]:
            error_message = error_details['message'] + " at " + error_details['location']
            report[error_message].append(resource_id)
    print_progressbar(**kwargs)


def print_progressbar(**kwargs):
    if 'iteration' in kwargs and 'total_count' in kwargs:
        iteration = kwargs["iteration"]
        total_count = kwargs["total_count"]
        percent = 100 * (iteration / total_count)
        filled_length = int(percent)
        bar = "#" * filled_length + '-' * (100 - filled_length)
        print("\rProcessing (%d/%d): |%s| %d%% Complete" % (iteration, total_count, bar, percent), end='\r')


def detail_message(server_message):
    detail_message = None
    if "message" in server_message:
        detail_message = server_message["message"]
    elif "errorMessage" in server_message:
        detail_message = server_message["errorMessage"]
    return detail_message


def show(report):
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
