import argparse
import json
from urllib.parse import quote
from cedar.utils import downloader, validator
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server",
                        choices=['local', 'staging', 'production'],
                        default='staging',
                        help="The type of CEDAR server")
    parser.add_argument("apikey", metavar="apiKey",
                        help="The API key used to query the CEDAR resource server")
    parser.add_argument("identifiers", metavar="ID", nargs='+',
                        help="The target CEDAR resource to validate.")
    args = parser.parse_args()
    server_address = get_server_address(args.server)
    api_key = args.apikey
    ids = args.identifiers

    report = create_empty_report()

    total_resources = len(ids)
    for index, id in enumerate(ids, start=1):
        if 'template' in id:
            validate_template(api_key, server_address, id, report, iteration=index, total_count=total_resources)
        elif 'element' in id:
            validate_element(api_key, server_address, id, report, iteration=index, total_count=total_resources)
        elif 'field' in id:
            pass
        elif 'instance' in id:
            validate_instance(api_key, server_address, id, report, iteration=index, total_count=total_resources)
        else:
            report_unknown_type(id, report)

    show(report)


def validate_template(api_key, server_address, template_id, report, **kwargs):
    template = get_template(api_key, server_address, template_id)
    request_url = server_address + "/command/validate?resource_type=template"
    status_code, server_message = validator.validate_template(api_key, template, request_url=request_url)
    consume(report, template_id, status_code, server_message, **kwargs)


def validate_element(api_key, server_address, element_id, report, **kwargs):
    element = get_element(api_key, server_address, element_id)
    request_url = server_address + "/command/validate?resource_type=element"
    status_code, server_message = validator.validate_element(api_key, element, request_url=request_url)
    consume(report, element_id, status_code, server_message, **kwargs)


def validate_instance(api_key, server_address, instance_id, report, **kwargs):
    instance = get_instance(api_key, server_address, instance_id)
    request_url = server_address + "/command/validate?resource_type=instance"
    status_code, server_message = validator.get_resource(api_key, instance, request_url=request_url)
    consume(report, instance_id, status_code, server_message, **kwargs)


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


def consume(report, resource_id, status_code, server_message, **kwargs):
    if status_code > 200:
        error_message = str(status_code) + " " + server_message["status"]
        if detail_message(server_message):
            error_message += " - " + detail_message(server_message)[:80] + "..."  # get a snippet
        report[error_message].append(resource_id)
    else:
        is_valid = server_message["validates"]
        if is_valid == 'false':
            error_messages = [error_details['message'] + " at " + error_details['location']
                              for error_details in server_message["errors"]]
            error_message = ', '.join(error_messages) # flatten list
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


def report_unknown_type(resource_id, report):
    report["Unknown type of resource to validate"].append(resource_id)


if __name__ == "__main__":
    main()
