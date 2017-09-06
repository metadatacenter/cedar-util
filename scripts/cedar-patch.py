import argparse
import requests.exceptions
from cedar.utils import getter, searcher, validator, get_server_address, to_json_string, write_to_file
from cedar.patch.collection import *
from cedar.patch.Engine import Engine


server_address = None
cedar_api_key = None
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
    parser.add_argument("--lookup",
                        required=False,
                        metavar="FILENAME",
                        help="An input file containing a list of resource identifiers to patch")
    parser.add_argument("--limit",
                        required=False,
                        type=int,
                        help="The maximum number of resources to validate")
    parser.add_argument("--output-dir",
                        required=False,
                        metavar="DIRNAME",
                        help="Set the output directory to store the patched resources")
    parser.add_argument("--debug",
                        required=False,
                        action="store_true",
                        help="Enter debug mode")
    parser.add_argument("apikey", metavar="CEDAR-API-KEY",
                        help="The API key used to query the CEDAR resource server")
    args = parser.parse_args()
    resource_type = args.type
    lookup_file = args.lookup
    limit = args.limit
    output_dir = args.output_dir
    debug = args.debug

    global server_address, cedar_api_key
    server_address = get_server_address(args.server)
    cedar_api_key = args.apikey

    patch_engine = build_patch_engine()
    if resource_type == 'template':
        template_ids = get_template_ids(lookup_file, limit)
        patch_template(patch_engine, template_ids, output_dir, debug)
    elif resource_type == 'element':
        pass
    elif resource_type == 'field':
        pass
    elif resource_type == 'instance':
        pass

    if not debug:
        show_report()


def build_patch_engine():
    patch_engine = Engine()
    patch_engine.add_patch(RenameValueLabelToRdfsLabelPatch())
    patch_engine.add_patch(AddSchemaDescriptionToContextPatch())
    patch_engine.add_patch(AddSchemaNameToContextPatch())
    patch_engine.add_patch(AddXsdToContextPatch())
    patch_engine.add_patch(AddRdfsLabelToContextPropertiesPatch())
    patch_engine.add_patch(AddRdfsToContextPropertiesPatch())
    patch_engine.add_patch(FillEmptyValuePatch())
    patch_engine.add_patch(AddSchemaVersionPatch())
    patch_engine.add_patch(NoMatchOutOfFourSchemasPatch())
    patch_engine.add_patch(NoMatchOutOfTwoSchemasPatch())
    patch_engine.add_patch(MoveContentToUiPatch())
    patch_engine.add_patch(RemoveArrayDuplicatesPatch())
    patch_engine.add_patch(AddIdToPropertiesPatch())
    patch_engine.add_patch(AddOrderToUiPatch())
    patch_engine.add_patch(AddPropertyLabelsToUiPatch())
    patch_engine.add_patch(AddProvenanceToContextPatch())
    patch_engine.add_patch(AddProvenanceToFieldOrElementPatch())
    patch_engine.add_patch(AddRequiredToFieldOrElementPatch())
    patch_engine.add_patch(AddValueConstraintsToFieldOrElementPatch())
    patch_engine.add_patch(RemoveEnumFromOneOfPatch())
    patch_engine.add_patch(RemoveEnumFromTypePatch())
    patch_engine.add_patch(RemoveIdFromPropertiesPatch())
    patch_engine.add_patch(RemoveValueFromPropertiesPatch())
    patch_engine.add_patch(RemovePageFromInnerUiPatch())
    patch_engine.add_patch(RecreateRequiredArrayPatch())
    patch_engine.add_patch(RemovePatternPropertiesPatch())
    patch_engine.add_patch(RestructureStaticTemplateFieldPatch())
    patch_engine.add_patch(RestructureMultiValuedFieldPatch())
    return patch_engine


def patch_template(patch_engine, template_ids, output_dir, debug):
    total_templates = len(template_ids)
    for counter, template_id in enumerate(template_ids, start=1):
        if not debug:
            print_progressbar(template_id, counter, total_templates)
        try:
            template = get_template(template_id)
            is_success, patched_template = patch_engine.execute(template, validate_template, debug=debug)
            if is_success:
                if patched_template is not None:
                    create_report("resolved", template_id)
                    filename = create_filename_from_id(template_id)
                    write_to_file(patched_template, filename, output_dir)
            else:
                create_report("unresolved", template_id)
                filename = create_filename_from_id(template_id)
                write_to_file(patched_template, filename, output_dir)
        except requests.exceptions.HTTPError as error:
            exit(error)


def validate_template(template):
    is_valid, message = validator.validate_template(server_address, cedar_api_key, template)
    return is_valid, [error_detail["message"] + " at " + error_detail["location"]
                      for error_detail in message["errors"]
                      if not is_valid]


def create_report(report_entry, template_id):
    report[report_entry].append(template_id)


def create_filename_from_id(resource_id):
    resource_hash = extract_resource_hash(resource_id)
    return "template-" + resource_hash + ".patched.json"


def print_progressbar(resource_id, counter, total_count):
    resource_hash = extract_resource_hash(resource_id)
    percent = 100 * (counter / total_count)
    filled_length = int(percent)
    bar = "#" * filled_length + '-' * (100 - filled_length)
    print("Patching (%d/%d): |%s| %d%% Complete [%s]" % (counter, total_count, bar, percent, resource_hash), end='\r')


def get_template_ids(lookup_file, limit):
    template_ids = []
    if lookup_file is not None:
        template_ids.extend(get_ids_from_file(lookup_file))
    else:
        template_ids = searcher.search_templates(server_address, cedar_api_key, max_count=limit)
    return template_ids


def get_ids_from_file(filename):
    with open(filename) as infile:
        resource_ids = infile.readlines()
        return [id.strip() for id in resource_ids]


def get_template(template_id):
    return getter.get_template(server_address, cedar_api_key, template_id)


def extract_resource_hash(resource_id):
    return resource_id[resource_id.rfind('/')+1:]


def show_report():
    resolved_size = len(report["resolved"])
    unresolved_size = len(report["unresolved"])
    print()
    print(create_report_message(resolved_size, unresolved_size))
    print()


def create_report_message(solved_size, unsolved_size):
    report_message = ""
    if unsolved_size == 0:
        report_message = "All templates were successfully patched."
    else:
        if solved_size == 0:
            report_message = "Unable to completely fix the invalid templates"
        else:
            total_size = solved_size + unsolved_size
            report_message += "Successfully fix %d out of %d invalid templates. (Success rate: %.0f%%)" % \
                              (solved_size, total_size, solved_size * 100 / total_size)
        report_message += "\n"
        report_message += "Details: " + to_json_string(dict(report))
    return report_message


if __name__ == "__main__":
    main()
