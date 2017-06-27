import argparse
import json
from urllib.parse import quote
from cedar.utils import downloader, validator, finder
from cedar.patch.collection import *
from cedar.patch.Engine import Engine


api_key = None


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
    parser.add_argument("--debug",
                        required=False,
                        action="store_true",
                        help="Enter debug mode")
    parser.add_argument("apikey", metavar="apiKey",
                        help="The API key used to query the CEDAR resource server")
    args = parser.parse_args()
    server_address = get_server_address(args.server)
    type = args.type
    limit = args.limit
    debug = args.debug

    global api_key
    api_key = args.apikey

    patch_engine = build_patch_engine()

    report = {
        "resolved": [],
        "unresolved": []
    }
    if type == 'template':
        patch_template(patch_engine, api_key, server_address, limit, report, debug)
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


def patch_template(patch_engine, api_key, server_address, limit, report, debug=False):
    template_ids = get_template_ids(api_key, server_address, limit)
    total_templates = len(template_ids)
    for index, template_id in enumerate(template_ids, start=1):
        if not debug:
            print_progressbar(template_id, iteration=index, total_count=total_templates)
        template = get_template(api_key, server_address, template_id)
        is_success = patch_engine.execute(template, template_validator, debug=debug)
        if is_success:
            report["resolved"].append(template_id)
        else:
            report["unresolved"].append(template_id)


def template_validator(template):
    url = "https://resource.staging.metadatacenter.net/command/validate?resource_type=template" # XXX: Should use the production server
    status_code, report = validator.validate_template(api_key, template, request_url=url)
    is_valid = json.loads(report["validates"])
    return is_valid, [ error_detail["message"] + " at " + error_detail["location"] for error_detail in report["errors"] if not is_valid ]


def print_progressbar(template_id, **kwargs):
    template_hash = template_id[template_id.rfind('/')+1:]
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


def get_server_address(server):
    server_address = "http://localhost"
    if server == 'local':
        server_address = "https://resource.metadatacenter.orgx"
    elif server == 'staging':
        server_address = "https://resource.staging.metadatacenter.net"
    elif server == 'production':
        server_address = "https://resource.metadatacenter.net"
    return server_address


def show(report):
    resolved_size = len(report["resolved"])
    unresolved_size = len(report["unresolved"])
    total_size = resolved_size + unresolved_size
    message = "All templates were successfully patched."
    if unresolved_size > 0:
        message = "Unable to patch %d out of %d templates. (Success rate: %.0f%%)" % \
                  (unresolved_size, total_size, resolved_size*100/total_size)
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
