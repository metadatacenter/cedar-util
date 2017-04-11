import argparse
import json
from urllib.parse import quote
from cedar.utils import downloader, validator, enumerator


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

    if type == 'template':
        validate_template(api_key, server_address, limit)
    elif type == 'element':
        validate_element(api_key, server_address, limit)
    elif type == 'field':
        pass
    elif type == 'instance':
        validate_instance(api_key, server_address, limit)
    else:
        print("Unknown type of resource to validate: " + type)


def validate_template(api_key, server_address, limit):
    template_ids = get_template_ids(api_key, server_address, limit)
    for template_id in template_ids:
        template = get_template(api_key, server_address, template_id)
        request_url = server_address + "/command/validate?resource_types=template"
        status_code, message = validator.validate_template(api_key, template, request_url=request_url)
        print(status_code, message)
        printout(status_code, message)


def validate_element(api_key, server_address, limit):
    element_ids = get_element_ids(api_key, server_address, limit)
    for element_id in element_ids:
        element = get_element(api_key, server_address, element_id)
        request_url = server_address + "/command/validate?resource_types=element"
        status_code, message = validator.validate_element(api_key, element, request_url=request_url)
        printout(status_code, message)


def validate_instance(api_key, server_address, limit):
    instance_ids = get_instance_ids(api_key, server_address, limit)
    for instance_id in instance_ids:
        instance = get_instance(api_key, server_address, instance_id)
        request_url = server_address + "/command/validate?resource_types=instance"
        status_code, message = validator.validate_instance(api_key, instance, request_url=request_url)
        printout(status_code, message)


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


def escape(s):
    return quote(str(s), safe='')


def to_json(obj):
    return json.loads(json.dumps(obj))


def printout(status_code, message):
    char = "."
    if status_code > 200:
        char = "X"
        print(message)
    else:
        is_valid = to_json(message)["validates"]
        if is_valid == 'false':
            char = "*"
    print(char, end="", flush=True)


if __name__ == "__main__":
    main()
