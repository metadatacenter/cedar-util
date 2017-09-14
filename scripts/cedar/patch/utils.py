import re
import dpath
import json


def is_template(resource, at=None):
    if at:
        resource = dpath.util.get(resource, at)
    resource_type = resource.get("@type")
    if resource_type:  # if exists
        return resource_type == "https://schema.metadatacenter.org/core/Template"
    else:
        return False


def is_template_field(resource, at=None):
    if at:
        resource = dpath.util.get(resource, at)
    resource_type = resource.get("@type")
    if resource_type:  # if exists
        return resource_type == "https://schema.metadatacenter.org/core/TemplateField"
    else:
        return False


def is_template_element(resource, at=None):
    if at:
        resource = dpath.util.get(resource, at)
    resource_type = resource.get("@type")
    if resource_type:  # if exists
        return resource_type == "https://schema.metadatacenter.org/core/TemplateElement"
    else:
        return False


def is_static_template_field(resource, at=None):
    if at:
        resource = dpath.util.get(resource, at)
    resource_type = resource.get("@type")
    if resource_type:  # if exists
        return resource_type == "https://schema.metadatacenter.org/core/StaticTemplateField"
    else:
        return False


def is_multivalued_field(resource, at=None):
    if at:
        resource = dpath.util.get(resource, at)
    try:
        input_type = dpath.util.get(resource, "/_ui/inputType")
        multiple_choice = dpath.util.get(resource, "/_valueConstraints/multipleChoice")
        if input_type and multiple_choice: # if both parameters present
            return (input_type == "list" or input_type == "checkbox") and multiple_choice == True
    except KeyError:
        pass  # Ignore
    return False


def get_json_object(doc, at):
    json_object = {}
    value = dpath.util.get(doc, at)
    if isinstance(value, dict):
        json_object = value
    return json_object


def to_json(string):
    return json.loads(string)


def get_parent_path(path):
    return path[:path.rfind('/')]


def get_error_location(text):
    found = ''
    try:
        found = re.search('at (/.+?)$', text).group(1)
    except AttributeError:
        found = ''
    return found


def check_argument(argname, argobj, isreq=True):
    if isreq:
        if argobj is None:
            raise Exception("The method requires the '" + argname + "' argument")


def check_argument_not_none(argname, arg):
    if arg is None:
        raise Exception("The method requires the '" + argname + "' argument")
