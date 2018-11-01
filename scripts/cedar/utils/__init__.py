import json
import os


__all__ = [
    'get_server_address',
    'to_boolean',
    'to_json_string',
    'write_to_file'
]


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