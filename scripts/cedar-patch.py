import argparse
import json
from urllib.parse import quote
from cedar.utils import downloader, validator, finder
from cedar.patch.collection import *
from cedar.patch.Engine import Engine


server_address = None
cedar_api_key = None
staging_api_key = None
report = {
    "resolved": [],
    "unresolved": []
}


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
                        type=int,
                        help="The maximum number of resources to validate")
    parser.add_argument("--use-staging-validator",
                        required=False,
                        metavar="CEDAR-STAGING-API-KEY",
                        help="Use the validator from the staging server (nightly-build)")
    parser.add_argument("--outputDir",
                        required=False,
                        default="/tmp",
                        help="Set the output directory to store the patched resources")
    parser.add_argument("--debug",
                        required=False,
                        action="store_true",
                        help="Enter debug mode")
    parser.add_argument("apikey", metavar="CEDAR-API-KEY",
                        help="The API key used to query the CEDAR resource server")
    args = parser.parse_args()
    type = args.type
    limit = args.limit
    output_dir = args.targetDir
    debug = args.debug

    global server_address, cedar_api_key, staging_api_key
    server_address = get_server_address(args.server)
    cedar_api_key = args.apikey
    staging_api_key = args.use_staging_validator

    patch_engine = build_patch_engine()
    if type == 'template':
        patch_template(patch_engine, limit, output_dir, debug)
    elif type == 'element':
        pass
    elif type == 'field':
        pass
    elif type == 'instance':
        pass

    show(report)


def build_patch_engine():
    patch_engine = Engine()
    patch_engine.add_patch(FillEmptyValuePatch())
    patch_engine.add_patch(AddSchemaVersionPatch())
    patch_engine.add_patch(NoMatchOutOfFourSchemasPatch())
    patch_engine.add_patch(NoMatchOutOfTwoSchemasPatch())
    patch_engine.add_patch(MoveContentToUiPatch())
    patch_engine.add_patch(RemoveArrayDuplicatesPatch())
    patch_engine.add_patch(AddIdToPropertiesPatch())
    patch_engine.add_patch(AddOrderToUiPatch())
    patch_engine.add_patch(AddPropertyLabelsToUiPatch())
    patch_engine.add_patch(AddProvenanceToFieldOrElementPatch())
    patch_engine.add_patch(AddRequiredToFieldOrElementPatch())
    patch_engine.add_patch(AddValueConstraintsToFieldOrElementPatch())
    patch_engine.add_patch(RemoveEnumFromOneOfPatch())
    patch_engine.add_patch(RemoveEnumFromTypePatch())
    patch_engine.add_patch(RemoveIdFromPropertiesPatch())
    patch_engine.add_patch(RemoveValueFromPropertiesPatch())
    patch_engine.add_patch(RemovePageFromInnerUiPatch())
    patch_engine.add_patch(RecreateRequiredArrayPatch())
    patch_engine.add_patch(RestructureStaticTemplateFieldPatch())
    return patch_engine


def patch_template(patch_engine, limit, output_dir, debug=False):
    template_ids = get_template_ids(cedar_api_key, server_address, limit)
    total_templates = len(template_ids)
    for index, template_id in enumerate(template_ids, start=1):
        if not debug:
            print_progressbar(template_id, iteration=index, total_count=total_templates)
        template = get_template(cedar_api_key, server_address, template_id)
        is_success, patched_template = patch_engine.execute(template, validate_template, debug=debug)
        if is_success:
            if patched_template is not None:
                create_report("resolved", patched_template)
                write_to_file(patched_template, output_dir)
        else:
            create_report("unresolved", patched_template)
            write_to_file(patched_template, output_dir)


def validate_template(template):
    status_code, report = run_validator(template)
    is_valid = json.loads(report["validates"])
    return is_valid, [ error_detail["message"] + " at " + error_detail["location"] for error_detail in report["errors"] if not is_valid ]


def run_validator(template):
    return validator.validate_template(
        get_api_key(),
        template,
        request_url=get_validator_endpoint())


def create_report(report_entry, patched_template):
    report[report_entry].append(patched_template["@id"])


def write_to_file(patched_template, output_dir):
    if patched_template is not None:
        filename = create_filename_from_id(patched_template["@id"])
        if output_dir is None:
            output_dir = "/tmp"
        output_path = output_dir + "/" + filename
        with open(output_path, "w") as outfile:
            json.dump(patched_template, outfile)


def create_filename_from_id(resource_id):
    resource_hash = extract_resource_hash(resource_id)
    return resource_hash + ".patched.json"


def get_validator_endpoint():
    url = server_address + "/command/validate?resource_type=template"
    if staging_api_key is not None:
        url = "https://resource.staging.metadatacenter.net/command/validate?resource_type=template"
    return url


def get_api_key():
    api_key = cedar_api_key
    if staging_api_key is not None:
        api_key = staging_api_key
    return api_key


def print_progressbar(template_id, **kwargs):
    template_hash = extract_resource_hash(template_id)
    if 'iteration' in kwargs and 'total_count' in kwargs:
        iteration = kwargs["iteration"]
        total_count = kwargs["total_count"]
        percent = 100 * (iteration / total_count)
        filled_length = int(percent)
        bar = "#" * filled_length + '-' * (100 - filled_length)
        print("\rPatching (%d/%d): |%s| %d%% Complete [%s]" % (iteration, total_count, bar, percent, template_hash), end='\r')


def get_template_ids(api_key, server_address, limit):
    request_url = server_address + "/search?q=*&resource_types=template"
    return finder.all_templates(api_key, request_url, max_count=limit)


def get_template(api_key, server_address, template_id):
    request_url = server_address + "/templates/" + escape(template_id)
    return downloader.get_resource(api_key, request_url)


def escape(s):
    return quote(str(s), safe='')


def extract_resource_hash(resource_id):
    return resource_id[resource_id.rfind('/')+1:]


def get_server_address(server):
    address = "http://localhost"
    if server == 'local':
        address = "https://resource.metadatacenter.orgx"
    elif server == 'staging':
        address = "https://resource.staging.metadatacenter.net"
    elif server == 'production':
        address = "https://resource.metadatacenter.net"
    return address


def show(report):
    resolved_size = len(report["resolved"])
    unresolved_size = len(report["unresolved"])
    total_size = resolved_size + unresolved_size
    message = "All templates were successfully patched."
    if unresolved_size > 0:
        message = "Successfully patch %d out of %d invalid templates. (Success rate: %.0f%%)" % \
                  (resolved_size, total_size, resolved_size*100/total_size)
        message += "\n"
        message += "Details: " + to_json_string(dict(report))
    print("\n" + message)
    print()


def to_json_string(obj, pretty=True):
    if pretty:
        return json.dumps(obj, indent=2, sort_keys=True)
    else:
        return json.dumps(obj)


if __name__ == "__main__":
    main()
