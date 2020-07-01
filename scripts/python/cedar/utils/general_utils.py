import re
import dpath
import json
from distutils.version import StrictVersion
import cedar.patch2.constants as const
import os


def is_compatible(resource, required_version):
    current_schema_version = resource.get("schema:schemaVersion")
    return StrictVersion(current_schema_version) >= StrictVersion(required_version)


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


def is_instance(resource, at=None):
    if at:
        resource = dpath.util.get(resource, at)
    resource_type = resource.get("schema:isBasedOn")
    if resource_type:  # if exists
        return True
    else:
        return False


def get_resource_type(resource):
    if is_template(resource):
        return const.RESOURCE_TYPE_TEMPLATE
    elif is_template_element(resource):
        return const.RESOURCE_TYPE_TEMPLATE_ELEMENT
    elif is_template_field(resource):
        return const.RESOURCE_TYPE_TEMPLATE_FIELD
    elif is_instance(resource):
        return const.RESOURCE_TYPE_TEMPLATE_INSTANCE
    else:
        raise NameError('Resource type not found for resource: ' + resource)

def get_resource_type_from_id(resource_id):
    if 'templates' in resource_id:
        return const.RESOURCE_TYPE_TEMPLATE
    elif 'template-elements' in resource_id:
        return const.RESOURCE_TYPE_TEMPLATE_ELEMENT
    elif 'template-fields' in resource_id:
        return const.RESOURCE_TYPE_TEMPLATE_FIELD
    elif 'template-instances' in resource_id:
        return const.RESOURCE_TYPE_TEMPLATE_INSTANCE
    else:
        raise NameError('Resource type not found in resource id: ' + resource_id)


def get_mongodb_collection_name_from_resource_type(resource_type):
    if resource_type == const.RESOURCE_TYPE_TEMPLATE:
        return const.MONGODB_TEMPLATE_COLLECTION
    elif resource_type == const.RESOURCE_TYPE_TEMPLATE_ELEMENT:
        return const.MONGODB_TEMPLATE_ELEMENT_COLLECTION
    elif resource_type == const.RESOURCE_TYPE_TEMPLATE_FIELD:
        return const.MONGODB_TEMPLATE_FIELD_COLLECTION
    elif resource_type == const.RESOURCE_TYPE_TEMPLATE_INSTANCE:
        return const.MONGODB_TEMPLATE_INSTANCE_COLLECTION
    else:
        raise NameError('Resource type not found: ' + resource_type)


def matches_target_resource_types(resource, target_resource_types):
    if get_resource_type(resource) in target_resource_types:
        return True
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


def get_json_node(doc, at):
    json_node = None
    if at == '':
        json_node = doc
    else:
        values = dpath.util.values(doc, at)
        if values:  # if some values are present
            json_node = values[0]  # get the first element
    return json_node


def path_exists(doc, path):
    return dpath.util.values(doc, path)


def to_json(string):
    return json.loads(string)


def get_parent_object(doc, at):
    parent_path = get_parent_path(at)
    return get_json_node(doc, parent_path), parent_path


def get_parent_path(path):
    return path[:path.rfind('/')]


def get_error_location(text):
    found = ''
    try:
        found = re.search('at (/.+?)$', text).group(1)
    except AttributeError:
        found = ''
    return found


def jsonpath_to_xpath(path):
    """
    Converts a path in Json Path format (dot based) to Json Patch format (slash based)
    :param pathDotNotation:
    :return:
    """
    return '/' + path.replace('.', "/")

def get_server_address(alias):
    address = "http://localhost"
    if alias == 'local':
        address = "https://resource.metadatacenter.orgx"
    elif alias == 'staging':
        address = "https://resource.staging.metadatacenter.org"
    elif alias == 'production':
        address = "https://resource.metadatacenter.org"
    return address


def to_boolean(value):
    if str(value).lower() in ("yes", "y", "true",  "t", "1"):
        return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))


def to_json_string(obj, pretty=True):
    if pretty:
        return json.dumps(obj, indent=2, sort_keys=True)
    else:
        return json.dumps(obj)


def write_to_file(patched_template, filename, output_dir=None):
    if output_dir is None:
        output_dir = os.getcwd()
    output_path = output_dir + "/" + filename
    with open(output_path, "w") as outfile:
        json.dump(patched_template, outfile)


def print_progressbar(resource_iri, progress_counter, total_count, message="Making a progress"):
    resource_hash = extract_resource_hash(resource_iri)
    percent = 100 * (progress_counter / total_count)
    filled_length = int(percent)
    bar = "#" * filled_length + '-' * (100 - filled_length)
    print("%s (%d/%d): |%s| %d%% Complete [%s]"
          % (message, progress_counter, total_count, bar, percent, resource_hash), end='\r')


def extract_resource_hash(iri):
    return iri[iri.rfind('/')+1:]