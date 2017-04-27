import argparse
import json
from urllib.parse import quote
from cedar.utils import downloader, validator, enumerator
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
                        help="The maximum number of resources to validate")
    parser.add_argument("apikey", metavar="apiKey",
                        help="The API key used to query the CEDAR resource server")
    args = parser.parse_args()
    server_address = get_server_address(args.server)
    type = args.type
    limit = args.limit
    api_key = args.apikey

    report = create_empty_report()

    if type == 'template':
        validate_template(api_key, server_address, limit, report)
    elif type == 'element':
        validate_element(api_key, server_address, limit, report)
    elif type == 'field':
        pass
    elif type == 'instance':
        validate_instance(api_key, server_address, limit, report)

    show(report)


def validate_template(api_key, server_address, limit, report):
    template_ids = get_template_ids(api_key, server_address, limit)
    for template_id in template_ids:
        template = get_template(api_key, server_address, template_id)
        request_url = server_address + "/command/validate?resource_types=template"
        status_code, message = validator.validate_template(api_key, template, request_url=request_url)
        consume(report, status_code=status_code, output_message=message, resource_id=template_id)


def validate_element(api_key, server_address, limit, report):
    element_ids = get_element_ids(api_key, server_address, limit)
    for element_id in element_ids:
        element = get_element(api_key, server_address, element_id)
        request_url = server_address + "/command/validate?resource_types=element"
        status_code, message = validator.validate_element(api_key, element, request_url=request_url)
        consume(report, status_code=status_code, output_message=message, resource_id=element_id)


def validate_instance(api_key, server_address, limit, report):
    instance_ids = get_instance_ids(api_key, server_address, limit)
    for instance_id in instance_ids:
        instance = get_instance(api_key, server_address, instance_id)
        request_url = server_address + "/command/validate?resource_types=instance"
        status_code, message = validator.validate_instance(api_key, instance, request_url=request_url)
        consume(report, status_code=status_code, output_message=message, resource_id=instance_id)


def get_element_ids(api_key, server_address, limit):
    request_url = server_address + "/search?q=*&resource_types=element"
    return enumerator.all_templates(api_key, request_url, max_count=limit)


def get_template_ids(api_key, server_address, limit):
    request_url = server_address + "/search?q=*&resource_types=template"
    return enumerator.all_templates(api_key, request_url, max_count=limit)


def get_instance_ids(api_key, server_address, limit):
    request_url = server_address + "/search?q=*&resource_types=instance"
    return enumerator.all_templates(api_key, request_url, max_count=limit)


def get_template(api_key, server_address, template_id):
    request_url = server_address + "/templates/" + escape(template_id)
    return downloader.get_resource(api_key, request_url)


def get_element(api_key, server_address, element_id):
    request_url = server_address + "/template-elements/" + escape(element_id)
    return downloader.get_resource(api_key, request_url)


def get_instance(api_key, server_address, instance_id):
    request_url = server_address + "/template-instances/" + escape(instance_id)
    return downloader.get_resource(api_key, request_url)


def get_server_address(server):
    server_address = "http://localhost"
    if server == 'local':
        server_address = "https://resource.metadatacenter.orgx"
    elif server == 'staging':
        server_address = "https://resource.staging.metadatacenter.net"
    elif server == 'production':
        server_address = "https://resource.metadatacenter.net"

    return server_address


def create_empty_report():
    return defaultdict(list)


def escape(s):
    return quote(str(s), safe='')


def to_json_string(obj, pretty=True):
    if pretty:
        return json.dumps(obj, indent=2, sort_keys=True)
    else:
        return json.dumps(obj)


def consume(report, **kwargs):
    status_code = kwargs["status_code"]
    output_message = kwargs["output_message"]
    resource_id = kwargs["resource_id"]

    indicator = "."  # means OK
    if status_code > 200:
        error_message = str(status_code) + " " + output_message["status"]
        if detail_message(output_message):
            error_message += " - " + detail_message(output_message)[:80] + "..."  # get a snippet
        report[error_message].append(resource_id)
        indicator = "X"  # means server error
    else:
        is_valid = output_message["validates"]
        if is_valid == 'false':
            error_messages = [error_details['message'] + " at " + error_details['location']
                              for error_details in output_message["errors"]]
            error_message = ', '.join(error_messages) # flatten list
            report[error_message].append(resource_id)
            indicator = "*"  # means validation error

    print(indicator, end="", flush=True)


def detail_message(output_message):
    detail_message = None
    if "message" in output_message:
        detail_message = output_message["message"]
    elif "errorMessage" in output_message:
        detail_message = output_message["errorMessage"]
    return detail_message


def show(report):
    report_size = len(report)
    message = "No error was found."
    if report_size > 0:
        message = "Found " + str(report_size) + " validation error(s)."
        message += "\n"
        message += "Details: " + to_json_string(dict(report))
    print("\n" + message)


if __name__ == "__main__":
    main()
