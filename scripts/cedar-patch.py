import argparse
import os
import json
from pymongo import MongoClient
from requests import HTTPError

from cedar.utils import validator, to_json_string, write_to_file, print_progressbar, extract_resource_hash
from cedar.patch.collection import *
from cedar.patch.Engine import Engine


cedar_template_collection = "templates"
cedar_element_collection = "template-elements"
cedar_field_collection = "template-fields"

cedar_server_address = "https://resource." + os.environ['CEDAR_HOST']
cedar_api_key = "apiKey " + os.environ['CEDAR_ADMIN_USER_API_KEY']
mongodb_conn = "mongodb://" + os.environ['CEDAR_MONGO_ROOT_USER_NAME'] + ":" + os.environ['CEDAR_MONGO_ROOT_USER_PASSWORD'] + "@localhost:27017/admin"
report = {
    "resolved": [],
    "unresolved": [],
    "error": []
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type",
                        choices=['template', 'element', 'field'],
                        default="template",
                        help="the type of CEDAR resource")
    parser.add_argument("--input-json",
                        required=False,
                        metavar="FILENAME",
                        help="an input file containing the resource to patch")
    parser.add_argument("--input-mongodb",
                        required=False,
                        default="cedar",
                        metavar="DBNAME",
                        help="set the MongoDB database where resources are located")
    parser.add_argument("--filter",
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
                        metavar="DBNAME",
                        help="set the MongoDB database name to store the patched resources")
    parser.add_argument("--debug",
                        required=False,
                        action="store_true",
                        help="print the debugging messages")
    args = parser.parse_args()
    resource_type = args.type
    input_file = args.input_json
    input_mongodb = args.input_mongodb
    filter_list = args.filter
    limit = args.limit
    output_dir = args.output_dir
    output_mongodb = args.output_mongodb
    debug = args.debug

    patch_engine = build_patch_engine()
    if input_file is not None:
        if resource_type == 'template':
            template = read_json(input_file)
            patch_template_from_json(patch_engine, template, output_dir, debug)
        elif resource_type == 'element':
            element = read_json(input_file)
            patch_element_from_json(patch_engine, element, output_dir, debug)
        elif resource_type == 'field':
            field = read_json(input_file)
            patch_field_from_json(patch_engine, field, output_dir, debug)
    elif input_mongodb is not None:
        mongodb_client = setup_mongodb_client(mongodb_conn)
        source_database = setup_source_database(mongodb_client, input_mongodb)
        target_database = setup_target_database(mongodb_client, output_mongodb)
        if resource_type == 'template':
            template_ids = read_list(filter_list) if filter_list is not None else get_resource_ids(source_database, cedar_template_collection, limit)
            patch_template(patch_engine, template_ids, source_database, output_dir, target_database, debug)
        elif resource_type == 'element':
            element_ids = read_list(filter_list) if filter_list is not None else get_resource_ids(source_database, cedar_element_collection, limit)
            patch_element(patch_engine, element_ids, source_database, output_dir, target_database, debug)
        elif resource_type == 'field':
            field_ids = read_list(filter_list) if filter_list is not None else get_resource_ids(source_database, cedar_field_collection, limit)
            patch_element(patch_engine, field_ids, source_database, output_dir, target_database, debug)

    if not debug:
        show_report()


def build_patch_engine():
    return build_patch_engine_v150_to_v160()


def build_patch_engine_v150_to_v160():
    patch_engine = Engine()
    return patch_engine


def build_patch_engine_v160():
    patch_engine = Engine()
    patch_engine.add_patch(AllowNullForInstanceId())
    patch_engine.add_patch(NotAllowNullForElementId())
    patch_engine.add_patch(NotAllowNullForControlledTermFieldId())
    patch_engine.add_patch(NotAllowNullForNestedControlledTermFieldId())
    patch_engine.add_patch(AddPavDerivedFromToPropertiesPatch())
    patch_engine.add_patch(AddPavDerivedFromToContextPropertiesPatch())
    return patch_engine


def build_patch_engine_v150():
    patch_engine = Engine()
    patch_engine.add_patch(AddSchemaPropsToPropertiesPatch())
    patch_engine.add_patch(AddProvenanceToPropertiesPatch())
    patch_engine.add_patch(RecreateTemplateRequiredPatch())
    patch_engine.add_patch(RecreateAdditionalValuePatch())
    patch_engine.add_patch(AddBiboToContextPatch())
    patch_engine.add_patch(AddBiboStatusPatch())
    patch_engine.add_patch(AddBiboVersionPatch())
    patch_engine.add_patch(AddVersioningPatch())
    patch_engine.add_patch(AddValueConstraintsToFieldOrElementPatch())
    patch_engine.add_patch(FillEmptyPropertyDescriptionPatch())
    patch_engine.add_patch(AddSkosToContextPatch())
    patch_engine.add_patch(AddSkosToContextPropertiesPatch())
    patch_engine.add_patch(AddSkosNotationToContextPropertiesPatch())
    patch_engine.add_patch(AddSkosPrefLabelToContextPatch())
    patch_engine.add_patch(AddSkosAltLabelToContextPatch())
    return patch_engine


def build_patch_engine_v140():
    patch_engine = Engine()
    patch_engine.add_patch(AddSchemaPropsToPropertiesPatch())
    patch_engine.add_patch(AddProvenanceToPropertiesPatch())
    patch_engine.add_patch(RecreateTemplateRequiredPatch())
    patch_engine.add_patch(RecreateAdditionalValuePatch())
    patch_engine.add_patch(AddBiboToContextPatch())
    patch_engine.add_patch(AddBiboStatusPatch())
    patch_engine.add_patch(AddBiboVersionPatch())
    patch_engine.add_patch(AddVersioningPatch())
    patch_engine.add_patch(AddValueConstraintsToFieldOrElementPatch())
    patch_engine.add_patch(FillEmptyPropertyDescriptionPatch())
    return patch_engine


def build_patch_engine_v130():
    patch_engine = Engine()
    patch_engine.add_patch(RenameValueLabelToRdfsLabelPatch())
    patch_engine.add_patch(AddMissingContextPatch())
    patch_engine.add_patch(AddMultipleChoiceToValueConstraintsPatch())
    patch_engine.add_patch(AddSchemaIsBasedOnToContextPropertiesPatch())
    patch_engine.add_patch(AddSchemaDescriptionToContextPatch())
    patch_engine.add_patch(AddSchemaDescriptionToContextPropertiesPatch())
    patch_engine.add_patch(AddSchemaNameToContextPatch())
    patch_engine.add_patch(AddSchemaNameToContextPropertiesPatch())
    patch_engine.add_patch(AddSchemaPropsToPropertiesPatch())
    patch_engine.add_patch(AddSchemaToContextPatch())
    patch_engine.add_patch(AddXsdToContextPatch())
    patch_engine.add_patch(AddXsdToContextPropertiesPatch())
    patch_engine.add_patch(AddRdfsLabelToContextPropertiesPatch())
    patch_engine.add_patch(AddRdfsLabelToPropertiesPatch())
    patch_engine.add_patch(AddRdfsToContextPropertiesPatch())
    patch_engine.add_patch(FillEmptyValuePatch())
    patch_engine.add_patch(FillNullValuePatch())
    patch_engine.add_patch(AddSchemaVersionPatch())
    patch_engine.add_patch(NoMatchOutOfFiveSchemasPatch())
    patch_engine.add_patch(NoMatchOutOfTwoSchemasPatch())
    patch_engine.add_patch(MoveTitleAndDescriptionPatch())
    patch_engine.add_patch(MoveTitlePatch())
    patch_engine.add_patch(MoveDescriptionPatch())
    patch_engine.add_patch(MoveContentToUiPatch())
    patch_engine.add_patch(RemoveArrayDuplicatesPatch())
    patch_engine.add_patch(AddIdToPropertiesPatch())
    patch_engine.add_patch(AddContentToUiPatch())
    patch_engine.add_patch(AddOrderToUiPatch())
    patch_engine.add_patch(AddPropertyLabelsToUiPatch())
    patch_engine.add_patch(AddProvenanceToContextPatch())
    patch_engine.add_patch(AddProvenanceToContextPropertiesPatch())
    patch_engine.add_patch(AddProvenanceToFieldOrElementPatch())
    patch_engine.add_patch(AddProvenanceToPropertiesPatch())
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
    patch_engine.add_patch(RemoveSelectionTypeFromUiPatch())
    patch_engine.add_patch(RemoveTemplateIdFromPropertiesPatch())
    patch_engine.add_patch(RemoveUiFromPropertiesPatch())
    patch_engine.add_patch(RestructureStaticTemplateFieldPatch())
    patch_engine.add_patch(RestructureMultiValuedFieldPatch())
    patch_engine.add_patch(AddBiboToContextPatch())
    patch_engine.add_patch(AddVersioningPatch())
    patch_engine.add_patch(AddVersioningInNestedElementPatch())
    patch_engine.add_patch(AddVersioningInNestedMultiElementPatch())
    return patch_engine


def patch_template_from_json(patch_engine, template, output_dir, debug=False):
    try:
        template_id = template["@id"]
        is_success, patched_template = patch_engine.execute(template, validate_template_callback, debug=debug)
        if is_success:
            if patched_template is not None:
                create_report("resolved", template_id)
                if output_dir is not None:
                    filename = create_filename_from_id(template_id, prefix="template-patched-")
                    write_to_file(patched_template, filename, output_dir)
        else:
            create_report("unresolved", template_id)
            if output_dir is not None:
                filename = create_filename_from_id(template_id, prefix="template-partially-patched-")
                write_to_file(patched_template, filename, output_dir)
    except (HTTPError, KeyError) as error:
        create_report("error", [template_id, "Error details: " + str(error)])
    print()  # console printing separator


def patch_template(patch_engine, template_ids, source_database, output_dir=None, target_database=None, debug=False):
    total_templates = len(template_ids)
    for counter, template_id in enumerate(template_ids, start=1):
        if not debug:
            print_progressbar(template_id, counter, total_templates, message="Patching")
        try:
            template = read_from_mongodb(source_database, cedar_template_collection, template_id)
            is_success, patched_template = patch_engine.execute(template, validate_template_callback, debug=debug)
            if is_success:
                if patched_template is not None:
                    create_report("resolved", template_id)
                    if output_dir is not None:
                        filename = create_filename_from_id(template_id, prefix="template-patched-")
                        write_to_file(patched_template, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, cedar_template_collection, patched_template)
                else:
                    if output_dir is not None:
                        filename = create_filename_from_id(template_id, prefix="template-")
                        write_to_file(template, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, cedar_template_collection, template)
            else:
                create_report("unresolved", template_id)
                if output_dir is not None:
                    if patched_template is None:
                        patched_template = template
                    filename = create_filename_from_id(template_id, prefix="template-partially-patched-")
                    write_to_file(patched_template, filename, output_dir)
                if target_database is not None: # Save the original to the database
                    write_to_mongodb(target_database, cedar_template_collection, template)
        except (HTTPError, KeyError) as error:
            create_report("error", [template_id, "Error details: " + str(error)])
    print()  # console printing separator


def validate_template_callback(template):
    is_valid, message = validator.validate_template(cedar_server_address, cedar_api_key, template)
    return is_valid, [error_detail["message"] + " at " + error_detail["location"]
                      for error_detail in message["errors"]
                      if not is_valid]


def patch_element_from_json(patch_engine, element, output_dir, debug):
    try:
        element_id = element["@id"]
        is_success, patched_element = patch_engine.execute(element, validate_element_callback, debug=debug)
        if is_success:
            if patched_element is not None:
                create_report("resolved", element_id)
                if output_dir is not None:
                    filename = create_filename_from_id(element_id, prefix="element-patched-")
                    write_to_file(patched_element, filename, output_dir)
        else:
            create_report("unresolved", element_id)
            if output_dir is not None:
                filename = create_filename_from_id(element_id, prefix="element-partially-patched-")
                write_to_file(patched_element, filename, output_dir)
    except (HTTPError, KeyError, TypeError) as error:
        create_report("error", [element_id, "Error details: " + str(error)])


def patch_element(patch_engine, element_ids, source_database, output_dir=None, target_database=None, debug=False):
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        if not debug:
            print_progressbar(element_id, counter, total_elements, message="Patching")
        try:
            element = read_from_mongodb(source_database, cedar_element_collection, element_id)
            is_success, patched_element = patch_engine.execute(element, validate_element_callback, debug=debug)
            if is_success:
                if patched_element is not None:
                    create_report("resolved", element_id)
                    if output_dir is not None:
                        filename = create_filename_from_id(element_id, prefix="element-patched-")
                        write_to_file(patched_element, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, cedar_element_collection, patched_element)
                else:
                    if output_dir is not None:
                        filename = create_filename_from_id(element_id, prefix="element-")
                        write_to_file(element, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, cedar_element_collection, element)
            else:
                create_report("unresolved", element_id)
                if output_dir is not None:
                    if patched_element is None:
                        patched_element = element
                    filename = create_filename_from_id(element_id, prefix="element-partially-patched-")
                    write_to_file(patched_element, filename, output_dir)
                if target_database is not None: # Save the original to the database
                    write_to_mongodb(target_database, cedar_element_collection, element)
        except (HTTPError, KeyError, TypeError) as error:
            create_report("error", [element_id, "Error details: " + str(error)])
    print()  # console printing separator


def validate_element_callback(element):
    is_valid, message = validator.validate_element(cedar_server_address, cedar_api_key, element)
    return is_valid, [error_detail["message"] + " at " + error_detail["location"]
                      for error_detail in message["errors"]
                      if not is_valid]


def patch_field_from_json(patch_engine, field, output_dir, debug):
    try:
        field_id = field["@id"]
        is_success, patched_field = patch_engine.execute(field, validate_field_callback, debug=debug)
        if is_success:
            if patched_field is not None:
                create_report("resolved", field_id)
                if output_dir is not None:
                    filename = create_filename_from_id(field_id, prefix="field-patched-")
                    write_to_file(patched_field, filename, output_dir)
        else:
            create_report("unresolved", field_id)
            if output_dir is not None:
                filename = create_filename_from_id(field_id, prefix="field-partially-patched-")
                write_to_file(patched_field, filename, output_dir)
    except (HTTPError, KeyError, TypeError) as error:
        create_report("error", [field_id, "Error details: " + str(error)])


def patch_field(patch_engine, field_ids, source_database, output_dir=None, target_database=None, debug=False):
    total_fields = len(field_ids)
    for counter, field_id in enumerate(field_ids, start=1):
        if not debug:
            print_progressbar(field_id, counter, total_fields, message="Patching")
        try:
            field = read_from_mongodb(source_database, cedar_field_collection, field_id)
            is_success, patched_field = patch_engine.execute(field, validate_field_callback, debug=debug)
            if is_success:
                if patched_field is not None:
                    create_report("resolved", field_id)
                    if output_dir is not None:
                        filename = create_filename_from_id(field_id, prefix="field-patched-")
                        write_to_file(patched_field, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, cedar_field_collection, patched_field)
                else:
                    if output_dir is not None:
                        filename = create_filename_from_id(field_id, prefix="field-")
                        write_to_file(field, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, cedar_field_collection, field)
            else:
                create_report("unresolved", field_id)
                if output_dir is not None:
                    if patched_field is None:
                        patched_field = field
                    filename = create_filename_from_id(field_id, prefix="field-partially-patched-")
                    write_to_file(patched_field, filename, output_dir)
                if target_database is not None: # Save the original to the database
                    write_to_mongodb(target_database, cedar_field_collection, field)
        except (HTTPError, KeyError, TypeError) as error:
            create_report("error", [field_id, "Error details: " + str(error)])
    print()  # console printing separator


def validate_field_callback(field):
    is_valid, message = validator.validate_field(cedar_server_address, cedar_api_key, field)
    return is_valid, [error_detail["message"] + " at " + error_detail["location"]
                      for error_detail in message["errors"]
                      if not is_valid]


def setup_mongodb_client(mongodb_conn):
    if mongodb_conn is None:
        return None
    return MongoClient(mongodb_conn)


def setup_source_database(mongodb_client, source_db_name):
    if mongodb_client is None or source_db_name is None:
        return None

    db_names = mongodb_client.list_database_names()
    if source_db_name not in db_names:
        print(" ERROR    | Input MongoDB database not found: " + source_db_name)
        exit(0)

    return mongodb_client[source_db_name]


def setup_target_database(mongodb_client, output_mongodb):
    if mongodb_client is None or output_mongodb is None:
        return None

    if output_mongodb == "cedar":
        raise Exception("Refused to store the patched resources into the main 'cedar' database")

    db_names = mongodb_client.database_names()
    if output_mongodb in db_names:
        if confirm("The patch database '" + output_mongodb + "' already exists. Drop the content to proceed (Y/[N])?", default_response=False):
            print("Dropping database...")
            mongodb_client.drop_database(output_mongodb)
        else:
            exit(0)

    mongodb_client.admin.command("copydb", fromdb="cedar", todb=output_mongodb)

    return mongodb_client[output_mongodb]


def get_db_name(mongodb_conn):
    return mongodb_conn[mongodb_conn.rfind("/")+1:]


def write_to_mongodb(database, collection_name, resource):
    database[collection_name].replace_one({'@id': resource['@id']}, pre_write(resource))


def pre_write(resource):
    new = {}
    for k, v in resource.items():
        if isinstance(v, dict):
            v = pre_write(v)
        new[k.replace('$schema', '_$schema')] = v
    return new


def create_report(report_entry, template_id):
    report[report_entry].append(template_id)


def create_filename_from_id(resource_id, prefix=""):
    resource_hash = extract_resource_hash(resource_id)
    return prefix + resource_hash + ".json"


def get_resource_ids(database, collection_name, limit):
    resource_ids = []
    if limit:
        found_ids = database[collection_name].distinct("@id").limit(limit)
        resource_ids.extend(found_ids)
    else:
        found_ids = database[collection_name].distinct("@id")
        resource_ids.extend(found_ids)
    filtered_ids = filter(lambda x: x is not None, resource_ids)
    return list(filtered_ids)


def read_list(filename):
    with open(filename) as infile:
        resource_ids = infile.readlines()
        return [id.strip() for id in resource_ids]


def read_json(filename):
    with open(filename) as infile:
        content = json.load(infile)
        return content


def read_from_mongodb(database, collection_name, resource_id):
    resource = database[collection_name].find_one({'@id': resource_id})
    return post_read(resource)


def post_read(resource):
    new = {}
    for k, v in resource.items():
        if k == '_id':
            continue
        if isinstance(v, dict):
            v = post_read(v)
        new[k.replace('_$schema', '$schema')] = v
    return new


def show_report():
    resolved_size = len(report["resolved"])
    unresolved_size = len(report["unresolved"])
    error_size = len(report["error"])
    print()
    print(create_report_message(resolved_size, unresolved_size, error_size))
    print()


def create_report_message(solved_size, unsolved_size, error_size):
    report_message = ""
    if unsolved_size == 0 and error_size == 0:
        report_message = "All resources were successfully patched."
    else:
        if solved_size == 0:
            report_message = "Unable to completely fix the invalid resources"
        else:
            total_size = solved_size + unsolved_size + error_size
            report_message += "Successfully fix %d out of %d invalid resources. (Success rate: %.0f%%)" % \
                              (solved_size, total_size, solved_size * 100 / total_size)
        report_message += "\n"
        report_message += "Details: " + to_json_string(dict(report))
    return report_message


def confirm(prompt, default_response=False):
    while True:
        answer = input(prompt)
        if answer == "":
            return default_response
        else:
            if answer == "y" or answer == "Y" or answer == "yes" or answer == "Yes":
                return True
            elif answer == "n" or answer == "N" or answer == "no" or answer == "No":
                return False
            else:
                continue


if __name__ == "__main__":
    main()
