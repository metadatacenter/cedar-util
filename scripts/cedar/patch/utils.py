import json
import re
from urllib.parse import quote
from cedar.utils import downloader, validator, finder


def get_template(template_id):
    api_key = "apiKey 207d5c77b5726363145fbcd6253268d2363f59fc20648ff9bf0650da49a02b27"
    url = "https://resource.staging.metadatacenter.net/templates/" + escape(template_id)
    return downloader.get_resource(api_key, url)


def validate_template(template):
    api_key = "apiKey 8b9e3e4d8f0aa726e27aa314174b6d5491bbdf77f2bca6e796d6f0ef8ec6dee4"
    url = "https://resource.metadatacenter.net/command/validate?resource_type=template"
    status_code, message = validator.validate_template(api_key, template, request_url=url)
    is_valid = json.loads(message["validates"])
    return is_valid, [ error["message"] + " at " + error["location"] for error in message["errors"] if not is_valid ]


def get_all_templates():
    api_key = "apiKey 207d5c77b5726363145fbcd6253268d2363f59fc20648ff9bf0650da49a02b27"
    url = "https://resource.staging.metadatacenter.net/search?q=*&resource_types=template"
    template_list = finder.all_templates(api_key, request_url=url)
    return template_list


def escape(s):
    return quote(str(s), safe='')


def get_paths(data, pattern=None):
    output = set()
    walk(output, "", data)
    if pattern is not None:
        pattern = re.compile(pattern)
        output = [element for element in output if pattern.match(element)]
    return output


def walk(output, path, data):
    for k, v in data.items():
        if isinstance(v, dict):
            output.add(path + "/" + k)
            walk(output, path + "/" + k, v)
        else:
            output.add(path + "/" + k)


def get_error_location(text):
    found = ''
    try:
        found = re.search('at (/.+?)$', text).group(1)
    except AttributeError:
        found = ''
    return found
