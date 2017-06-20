import argparse
import json
from urllib.parse import quote
from cedar.utils import downloader, finder
from cedar.patch.collection import *
from cedar.patch.Engine import Engine


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
    api_key = args.apikey

    patch_engine = build_patch_engine()

    report = {
        "success": [],
        "failed": []
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
    patch_engine.add_patch(AddIdToPropertiesPatch())
    patch_engine.add_patch(AddOrderToUiPatch())
    patch_engine.add_patch(AddPropertyLabelsToUiPatch())
    patch_engine.add_patch(FillEmptyValuePatch())
    patch_engine.add_patch(RecreateRequiredArrayPatch())
    patch_engine.add_patch(RemoveArrayDuplicatesPatch())
    patch_engine.add_patch(RemoveEnumFromOneOfPatch())
    patch_engine.add_patch(RemoveEnumFromTypePatch())
    patch_engine.add_patch(RemoveIdFromPropertiesPatch())
    patch_engine.add_patch(RemoveValueFromPropertiesPatch())
    return patch_engine


def patch_template(patch_engine, api_key, server_address, limit, report, debug=False):
    template_ids = get_template_ids(api_key, server_address, limit)
    total_templates = len(template_ids)
    for index, template_id in enumerate(template_ids, start=1):
        template = get_template(api_key, server_address, template_id)
        is_success = patch_engine.execute(template, debug=debug)
        if is_success:
            report["success"].append(template_id)
        else:
            report["failed"].append(template_id)

        if not debug:
            print_progressbar(iteration=index, total_count=total_templates)


def print_progressbar(**kwargs):
    if 'iteration' in kwargs and 'total_count' in kwargs:
        iteration = kwargs["iteration"]
        total_count = kwargs["total_count"]
        percent = 100 * (iteration / total_count)
        filled_length = int(percent)
        bar = "#" * filled_length + '-' * (100 - filled_length)
        print("\rPatching (%d/%d): |%s| %d%% Complete" % (iteration, total_count, bar, percent), end='\r')


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
    failed_size = len(report["failed"])
    message = "All templates were successfully patched."
    if failed_size > 0:
        message = "Unable to patch " + str(failed_size) + " template(s)."
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
