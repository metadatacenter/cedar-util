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
        if input_type == "checkbox":
            return True
        elif input_type == "list" and multiple_choice is True:
            return True
    except KeyError:
        pass  # Ignore
    return False


def get_json_object(doc, at):
    json_object = {}
    if at == '':
        json_object = doc
    else:
        values = dpath.util.values(doc, at)
        if values:  # if some values are present
            value = values[0]  # get the first element
            if isinstance(value, dict):
                json_object = value
    return json_object


def to_json(string):
    return json.loads(string)


def get_parent_object(doc, at):
    parent_path = get_parent_path(at)
    return get_json_object(doc, parent_path), parent_path


def get_parent_path(path):
    return path[:path.rfind('/')]


def get_error_location(text):
    found = ''
    try:
        found = re.search('at (/.+?)$', text).group(1)
    except AttributeError:
        found = ''
    return found
