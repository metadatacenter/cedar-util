import argparse
import json
from urllib.parse import quote
from cedar.utils import downloader, validator


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

    for id in ids:
        if 'template' in id:
            validate_template(api_key, server_address, id)
        elif 'element' in id:
            validate_element(api_key, server_address, id)
        elif 'field' in id:
            pass
        elif 'instance' in id:
            validate_instance(api_key, server_address, id)
        else:
            print("Unknown type of resource to validate: " + id)


def validate_template(api_key, server_address, template_id):
    template = get_template(api_key, server_address, template_id)
    request_url = server_address + "/command/validate?resource_types=template"
    message = validator.validate_template(api_key, template, request_url=request_url)
    printout(message)


def validate_element(api_key, server_address, element_id):
    element = get_element(api_key, server_address, element_id)
    request_url = server_address + "/command/validate?resource_types=element"
    message = validator.validate_element(api_key, element, request_url=request_url)
    printout(message)


def validate_instance(api_key, server_address, instance_id):
    instance = get_instance(api_key, server_address, instance_id)
    request_url = server_address + "/command/validate?resource_types=instance"
    message = validator.get_resource(api_key, instance, request_url=request_url)
    printout(message)


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
    return quote(s, safe='')


def to_json(obj):
    return json.loads(json.dumps(obj))


def printout(message):
    is_valid = to_json(message)["validates"]
    char = "."
    if is_valid == 'false':
        char = "*"
    print(char, end="")


if __name__ == "__main__":
    main()
