import argparse
from cedar.utils import getter, validator, get_server_address, to_json_string
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
    status_code, server_message = validator.validate_template(server_address, api_key, template)
    consume(report, template_id, status_code, server_message, **kwargs)


def validate_element(api_key, server_address, element_id, report, **kwargs):
    element = get_element(api_key, server_address, element_id)
    status_code, server_message = validator.validate_element(server_address, api_key, element)
    consume(report, element_id, status_code, server_message, **kwargs)


def validate_instance(api_key, server_address, instance_id, report, **kwargs):
    instance = get_instance(api_key, server_address, instance_id)
    status_code, server_message = validator.get_resource(server_address, api_key, instance)
    consume(report, instance_id, status_code, server_message, **kwargs)


def get_template(api_key, server_address, template_id):
    return getter.get_template(server_address, api_key, template_id)


def get_element(api_key, server_address, element_id):
    return getter.get_element(server_address, api_key, element_id)


def get_instance(api_key, server_address, instance_id):
    return getter.get_instance(server_address, api_key, instance_id)


def create_empty_report():
    return defaultdict(list)


def consume(report, resource_id, status_code, server_message, **kwargs):
    if status_code > 200:
        error_message = str(status_code) + " " + server_message["status"]
        if detail_message(server_message):
            error_message += " - " + detail_message(server_message)[:80] + "..."  # get a snippet
        report[error_message].append(resource_id)
    else:
        is_valid = server_message["validates"]
        if is_valid == 'false':
            for error_details in server_message["errors"]:
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


def report_unknown_type(resource_id, report):
    report["Unknown type of resource to validate"].append(resource_id)


if __name__ == "__main__":
    main()
