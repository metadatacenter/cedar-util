import argparse
import requests.exceptions
from pymongo import MongoClient
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
                        help="the type of CEDAR server")
    parser.add_argument("-t", "--type",
                        choices=['template', 'element', 'field', 'instance'],
                        default="template",
                        help="the type of CEDAR resource")
    parser.add_argument("--lookup",
                        required=False,
                        metavar="FILENAME",
                        help="an input file containing a list of resource identifiers to patch")
    parser.add_argument("--limit",
                        required=False,
                        type=int,
                        help="the maximum number of resources to patch")
    parser.add_argument("--output-dir",
                        required=False,
                        metavar="DIRNAME",
                        help="set the output directory to store the patched resources")
    parser.add_argument("--output-mongodb",
                        required=False,
                        metavar="DBCONN",
                        help="set the MongoDB connection URI to store the patched resources")
    parser.add_argument("--model-version",
                        required=False,
                        metavar="VERSION",
                        help="set the CEDAR model version of the patched resources")
    parser.add_argument("--keep-unresolved",
                        required=False,
                        action="store_true",
                        help="include the unresolved resources as part of the output")
    parser.add_argument("--debug",
                        required=False,
                        action="store_true",
                        help="print the debugging messages")
    parser.add_argument("apikey", metavar="CEDAR-API-KEY",
                        help="the API key used to access the CEDAR resource server")
    args = parser.parse_args()
    resource_type = args.type
    lookup_file = args.lookup
    limit = args.limit
    output_dir = args.output_dir
    mongo_database = setup_mongodb(args.output_mongodb)
    model_version = args.model_version

    keep_unresolved = args.keep_unresolved
    debug = args.debug

    global server_address, cedar_api_key
    server_address = get_server_address(args.server)
    cedar_api_key = args.apikey

    patch_engine = build_patch_engine()
    if resource_type == 'template':
        template_ids = get_template_ids(lookup_file, limit)
        patch_template(patch_engine, template_ids, model_version, output_dir, mongo_database, keep_unresolved, debug)
    elif resource_type == 'element':
        element_ids = get_element_ids(lookup_file, limit)
        patch_element(patch_engine, element_ids, model_version, output_dir, mongo_database, keep_unresolved, debug)
    elif resource_type == 'field':
        pass
    elif resource_type == 'instance':
        pass

    if not debug:
        show_report()


def build_patch_engine():
    patch_engine = Engine()
    patch_engine.add_patch(RenameValueLabelToRdfsLabelPatch())
    patch_engine.add_patch(AddSchemaIsBasedOnToContextPropertiesPatch())
    patch_engine.add_patch(AddSchemaDescriptionToContextPatch())
    patch_engine.add_patch(AddSchemaDescriptionToContextPropertiesPatch())
    patch_engine.add_patch(AddSchemaNameToContextPatch())
    patch_engine.add_patch(AddSchemaNameToContextPropertiesPatch())
    patch_engine.add_patch(AddSchemaToContextPatch())
    patch_engine.add_patch(AddXsdToContextPatch())
    patch_engine.add_patch(AddXsdToContextPropertiesPatch())
    patch_engine.add_patch(AddRdfsLabelToContextPropertiesPatch())
    patch_engine.add_patch(AddRdfsLabelToPropertiesPatch())
    patch_engine.add_patch(AddRdfsToContextPropertiesPatch())
    patch_engine.add_patch(FillEmptyValuePatch())
    patch_engine.add_patch(AddSchemaVersionPatch())
    patch_engine.add_patch(NoMatchOutOfFiveSchemasPatch())
    patch_engine.add_patch(NoMatchOutOfTwoSchemasPatch())
    patch_engine.add_patch(MoveTitleAndDescriptionPatch())
    patch_engine.add_patch(MoveContentToUiPatch())
    patch_engine.add_patch(RemoveArrayDuplicatesPatch())
    patch_engine.add_patch(AddIdToPropertiesPatch())
    patch_engine.add_patch(AddContentToUiPatch())
    patch_engine.add_patch(AddOrderToUiPatch())
    patch_engine.add_patch(AddPropertyLabelsToUiPatch())
    patch_engine.add_patch(AddProvenanceToContextPatch())
    patch_engine.add_patch(AddProvenanceToContextPropertiesPatch())
    patch_engine.add_patch(AddProvenanceToFieldOrElementPatch())
    patch_engine.add_patch(AddRequiredToFieldOrElementPatch())
    patch_engine.add_patch(AddValueConstraintsToFieldOrElementPatch())
    patch_engine.add_patch(RecreateTemplateRequiredPatch())
    patch_engine.add_patch(RecreateElementRequiredPatch())
    patch_engine.add_patch(RemoveEnumFromOneOfPatch())
    patch_engine.add_patch(RemoveEnumFromTypePatch())
    patch_engine.add_patch(RemoveIdFromPropertiesPatch())
    patch_engine.add_patch(RemoveInstanceOfPatch())
    patch_engine.add_patch(RemoveValueFromPropertiesPatch())
    patch_engine.add_patch(RemovePageFromInnerUiPatch())
    patch_engine.add_patch(RemovePatternPropertiesPatch())
    patch_engine.add_patch(RemovePavFromElementContextPropertiesPatch())
    patch_engine.add_patch(RemoveSchemaFromElementContextPropertiesPatch())
    patch_engine.add_patch(RemoveOslcFromElementContextPropertiesPatch())
    patch_engine.add_patch(RemoveXsdFromElementContextPropertiesPatch())
    patch_engine.add_patch(RemoveProvenanceFromPropertiesPatch())
    patch_engine.add_patch(RemoveSchemaDescriptionFromPropertiesPatch())
    patch_engine.add_patch(RemoveSchemaIsBasedOnFromPropertiesPatch())
    patch_engine.add_patch(RemoveSchemaNameFromPropertiesPatch())
    patch_engine.add_patch(RemoveSchemaVersionPatch())
    patch_engine.add_patch(RestructureStaticTemplateFieldPatch())
    patch_engine.add_patch(RestructureMultiValuedFieldPatch())
    return patch_engine


def patch_template(patch_engine, template_ids, model_version=None, output_dir=None, mongo_database=None,
                   keep_unresolved=False, debug=False):
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
                    if model_version is not None or model_version != "":
                        set_model_version(patched_template, model_version)
                    if output_dir is not None:
                        filename = create_filename_from_id(template_id, prefix="template-patched-")
                        write_to_file(patched_template, filename, output_dir)
                    if mongo_database is not None:
                        write_to_mongodb(mongo_database, "templates", patched_template)
            else:
                create_report("unresolved", template_id)
                if keep_unresolved:
                    if model_version is not None or model_version != "":
                        set_model_version(patched_template, model_version)
                    if output_dir is not None:
                        filename = create_filename_from_id(template_id, prefix="template-unresolved-")
                        write_to_file(patched_template, filename, output_dir)
                    if mongo_database is not None:
                        write_to_mongodb(mongo_database, "templates", patched_template)
                else:
                    if output_dir is not None:
                        filename = create_filename_from_id(template_id, prefix="template-original-")
                        write_to_file(template, filename, output_dir)
                    if mongo_database is not None:
                        write_to_mongodb(mongo_database, "templates", template)

        except requests.exceptions.HTTPError as error:
            exit(error)


def validate_template(template):
    is_valid, message = validator.validate_template(server_address, cedar_api_key, template)
    return is_valid, [error_detail["message"] + " at " + error_detail["location"]
                      for error_detail in message["errors"]
                      if not is_valid]


def patch_element(patch_engine, element_ids, model_version=None, output_dir=None, mongo_database=None,
                  keep_unresolved=False, debug=False):
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        if not debug:
            print_progressbar(element_id, counter, total_elements)
        try:
            element = get_element(element_id)
            is_success, patched_element = patch_engine.execute(element, validate_element, debug=debug)
            if is_success:
                if patched_element is not None:
                    create_report("resolved", element_id)
                    if model_version is not None or model_version != "":
                        set_model_version(patched_element, model_version)
                    if output_dir is not None:
                        filename = create_filename_from_id(element_id, prefix="element-patched-")
                        write_to_file(patched_element, filename, output_dir)
                    if mongo_database is not None:
                        write_to_mongodb(mongo_database, "template-elements", patched_element)
            else:
                create_report("unresolved", element_id)
                if keep_unresolved:
                    if model_version is not None or model_version != "":
                        set_model_version(patched_element, model_version)
                    if output_dir is not None:
                        filename = create_filename_from_id(element_id, prefix="element-unresolved-")
                        write_to_file(patched_element, filename, output_dir)
                    if mongo_database is not None:
                        write_to_mongodb(mongo_database, "templates", patched_element)
                else:
                    if output_dir is not None:
                        filename = create_filename_from_id(element_id, prefix="element-original-")
                        write_to_file(element, filename, output_dir)
                    if mongo_database is not None:
                        write_to_mongodb(mongo_database, "templates", element)

        except requests.exceptions.HTTPError as error:
            exit(error)


def validate_element(element):
    is_valid, message = validator.validate_element(server_address, cedar_api_key, element)
    return is_valid, [error_detail["message"] + " at " + error_detail["location"]
                      for error_detail in message["errors"]
                      if not is_valid]


def set_model_version(resource, model_version):
    for k, v in resource.items():
        if isinstance(v, dict):
            set_model_version(v, model_version)
        elif isinstance(v, str):
            if k == "schema:schemaVersion":
                resource[k] = model_version
                return


def setup_mongodb(mongodb_conn):
    if mongodb_conn is None:
        return None

    client = MongoClient(mongodb_conn)
    db_names = client.database_names()

    db_name = get_db_name(mongodb_conn)
    if db_name == "cedar":
        raise Exception("Refused to store the patched resources into the main 'cedar' database")

    if db_name in db_names:
        if confirm("The database '" + db_name + "' already exists. Drop the content ([Y]/N)?", yes_if_blank=True):
            print("Dropping database...")
            client.drop_database(db_name)

    return client[db_name]


def get_db_name(mongodb_conn):
    return mongodb_conn[mongodb_conn.rfind("/")+1:]


def write_to_mongodb(database, collection_name, resource):
    database[collection_name].insert_one(prepare(resource))


def prepare(resource):
    new = {}
    for k, v in resource.items():
        if isinstance(v, dict):
            v = prepare(v)
        new[k.replace('$schema', '_$schema')] = v
    return new


def create_report(report_entry, template_id):
    report[report_entry].append(template_id)


def create_filename_from_id(resource_id, prefix=""):
    resource_hash = extract_resource_hash(resource_id)
    return prefix + resource_hash + ".json"


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


def get_element_ids(lookup_file, limit):
    element_ids = []
    if lookup_file is not None:
        element_ids.extend(get_ids_from_file(lookup_file))
    else:
        element_ids = searcher.search_elements(server_address, cedar_api_key, max_count=limit)
    return element_ids


def get_ids_from_file(filename):
    with open(filename) as infile:
        resource_ids = infile.readlines()
        return [id.strip() for id in resource_ids]


def get_template(template_id):
    return getter.get_template(server_address, cedar_api_key, template_id)


def get_element(element_id):
    return getter.get_element(server_address, cedar_api_key, element_id)


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
        report_message = "All resources were successfully patched."
    else:
        if solved_size == 0:
            report_message = "Unable to completely fix the invalid resources"
        else:
            total_size = solved_size + unsolved_size
            report_message += "Successfully fix %d out of %d invalid resources. (Success rate: %.0f%%)" % \
                              (solved_size, total_size, solved_size * 100 / total_size)
        report_message += "\n"
        report_message += "Details: " + to_json_string(dict(report))
    return report_message


def confirm(prompt, yes_if_blank=False):
    while True:
        answer = input(prompt)
        if answer == "" and yes_if_blank:
            return True
        else:
            if answer == "y" or answer == "Y" or answer == "yes" or answer == "Yes":
                return True
            elif answer == "n" or answer == "N" or answer == "no" or answer == "No":
                return False
            else:
                continue


if __name__ == "__main__":
    main()
