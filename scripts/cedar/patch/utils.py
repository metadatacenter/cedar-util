import re
import dpath
from urllib.parse import quote


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
