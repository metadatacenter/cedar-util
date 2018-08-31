import argparse
import os
import json
from pymongo import MongoClient
from requests import HTTPError

from cedar.utils import validator, to_json_string, write_to_file
from cedar.patch.collection import *
from cedar.patch.Engine import Engine


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
                        choices=['template', 'element', 'field', 'instance'],
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
    parser.add_argument("--set-model-version",
                        required=False,
                        metavar="VERSION",
                        help="set the CEDAR model version of the patched resources")
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
    model_version = args.set_model_version
    debug = args.debug

    patch_engine = build_patch_engine()
    if input_file is not None:
        if resource_type == 'template':
            template = read_json(input_file)
            patch_template_from_json(patch_engine, template, model_version, output_dir, debug)
        elif resource_type == 'element':
            element = read_json(input_file)
            patch_element_from_json(patch_engine, element, model_version, output_dir, debug)
        elif resource_type == 'field':
            pass
        elif resource_type == 'instance':
            instance = read_json(input_file)
            patch_instance_from_json(instance, output_dir, debug)
    elif input_mongodb is not None:
        mongodb_client = setup_mongodb_client(mongodb_conn)
        source_database = setup_source_database(mongodb_client, input_mongodb)
        target_database = setup_target_database(mongodb_client, output_mongodb)
        if resource_type == 'template':
            template_ids = read_list(filter_list) if filter_list is not None else get_template_ids(source_database, limit)
            patch_template(patch_engine, template_ids, source_database, model_version, output_dir, target_database, debug)
        elif resource_type == 'element':
            element_ids = read_list(filter_list) if filter_list is not None else get_element_ids(source_database, limit)
            patch_element(patch_engine, element_ids, source_database, model_version, output_dir, target_database, debug)
        elif resource_type == 'field':
            pass
        elif resource_type == 'instance':
            instance_ids = read_list(filter_list) if filter_list is not None else get_instance_ids(source_database, limit)
            patch_instance(instance_ids, source_database, output_dir, target_database, debug)

    if not debug:
        show_report()


def build_patch_engine():
    return build_patch_engine_v130()


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


def patch_template_from_json(patch_engine, template, model_version, output_dir, debug=False):
    try:
        template_id = template["@id"]
        if model_version:
            set_model_version(template, model_version)
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


def patch_template(patch_engine, template_ids, source_database, model_version=None, output_dir=None, target_database=None, debug=False):
    total_templates = len(template_ids)
    for counter, template_id in enumerate(template_ids, start=1):
        if not debug:
            print_progressbar(template_id, counter, total_templates)
        try:
            template = get_template_from_mongodb(source_database, template_id)
            if model_version:
                set_model_version(template, model_version)
            is_success, patched_template = patch_engine.execute(template, validate_template_callback, debug=debug)
            if is_success:
                if patched_template is not None:
                    create_report("resolved", template_id)
                    if output_dir is not None:
                        filename = create_filename_from_id(template_id, prefix="template-patched-")
                        write_to_file(patched_template, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, "templates", patched_template)
                else:
                    if output_dir is not None:
                        filename = create_filename_from_id(template_id, prefix="template-")
                        write_to_file(template, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, "templates", template)
            else:
                create_report("unresolved", template_id)
                if output_dir is not None:
                    if patched_template is None:
                        patched_template = template
                    filename = create_filename_from_id(template_id, prefix="template-partially-patched-")
                    write_to_file(patched_template, filename, output_dir)
                if target_database is not None: # Save the original to the database
                    write_to_mongodb(target_database, "templates", template)
        except (HTTPError, KeyError) as error:
            create_report("error", [template_id, "Error details: " + str(error)])
    print()  # console printing separator


def validate_template_callback(template):
    is_valid, message = validator.validate_template(cedar_server_address, cedar_api_key, template)
    return is_valid, [error_detail["message"] + " at " + error_detail["location"]
                      for error_detail in message["errors"]
                      if not is_valid]


def patch_element_from_json(patch_engine, element, model_version, output_dir, debug):
    try:
        element_id = element["@id"]
        if model_version:
            set_model_version(element, model_version)
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


def patch_element(patch_engine, element_ids, source_database, model_version=None, output_dir=None, target_database=None, debug=False):
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        if not debug:
            print_progressbar(element_id, counter, total_elements)
        try:
            element = get_element_from_mongodb(source_database, element_id)
            if model_version:
                set_model_version(element, model_version)
            is_success, patched_element = patch_engine.execute(element, validate_element_callback, debug=debug)
            if is_success:
                if patched_element is not None:
                    create_report("resolved", element_id)
                    if output_dir is not None:
                        filename = create_filename_from_id(element_id, prefix="element-patched-")
                        write_to_file(patched_element, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, "template-elements", patched_element)
                else:
                    if output_dir is not None:
                        filename = create_filename_from_id(element_id, prefix="element-")
                        write_to_file(element, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, "template-elements", element)
            else:
                create_report("unresolved", element_id)
                if output_dir is not None:
                    if patched_element is None:
                        patched_element = element
                    filename = create_filename_from_id(element_id, prefix="element-partially-patched-")
                    write_to_file(patched_element, filename, output_dir)
                if target_database is not None: # Save the original to the database
                    write_to_mongodb(target_database, "template-elements", element)
        except (HTTPError, KeyError, TypeError) as error:
            create_report("error", [element_id, "Error details: " + str(error)])
    print()  # console printing separator


def validate_element_callback(element):
    is_valid, message = validator.validate_element(cedar_server_address, cedar_api_key, element)
    return is_valid, [error_detail["message"] + " at " + error_detail["location"]
                      for error_detail in message["errors"]
                      if not is_valid]


def patch_instance_from_json(instance, output_dir, debug=False):
    print(" WARNING  | Patching the instances might still leave some errors. Please run the validator manually to check thoroughly")
    try:
        instance_id = instance["@id"]
        patched_instance = fix_context(instance)
        patched_instance = rename(patched_instance, replace_valuelabel)

        create_report("resolved", instance_id)

        if output_dir is not None:
            filename = create_filename_from_id(instance_id, prefix="instance-patched-")
            write_to_file(patched_instance, filename, output_dir)
    except (HTTPError, KeyError) as error:
        create_report("error", [instance_id, "Error details: " + str(error)])
    print()  # console printing separator


def patch_instance(instance_ids, source_database, output_dir=None, target_database=None, debug=False):
    total_instances = len(instance_ids)
    print(" WARNING  | Patching the instances might still leave some errors. Please run the validator manually to check thoroughly")
    for counter, instance_id in enumerate(instance_ids, start=1):
        if not debug:
            print_progressbar(instance_id, counter, total_instances)
        try:
            instance = get_instance_from_mongodb(source_database, instance_id)
            patched_instance = fix_context(instance)
            patched_instance = rename(patched_instance, replace_valuelabel)

            create_report("resolved", instance_id)

            if output_dir is not None:
                filename = create_filename_from_id(instance_id, prefix="instance-patched-")
                write_to_file(patched_instance, filename, output_dir)
            if target_database is not None:
                write_to_mongodb(target_database, "template-instances", patched_instance)
        except (HTTPError, KeyError) as error:
            create_report("error", [instance_id, "Error details: " + str(error)])
    print()  # console printing separator


def fix_context(instance):
    context = instance["@context"]
    context["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#"
    context["xsd"] = "http://www.w3.org/2001/XMLSchema#"
    context["pav"] = "http://purl.org/pav/"
    context["schema"] = "http://schema.org/"
    context["oslc"] = "http://open-services.net/ns/core#"
    context["rdfs:label"] = {"@type": "xsd:string"}
    context["schema:isBasedOn"] = {"@type": "@id"}
    context["schema:name"] = {"@type": "xsd:string"}
    context["schema:description"] = {"@type": "xsd:string"}
    context["pav:createdOn"] = {"@type": "xsd:dateTime"}
    context["pav:createdBy"] = {"@type": "@id"}
    context["pav:lastUpdatedOn"] = {"@type": "xsd:dateTime"}
    context["oslc:modifiedBy"] = {"@type": "@id"}
    return instance


def rename(obj, replace_function):
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[replace_function(k)] = rename(v, replace_function)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(rename(v, replace_function) for v in obj)
    else:
        return obj
    return new


def replace_valuelabel(k):
    return k.replace('_valueLabel', 'rdfs:label')


def set_model_version(resource, model_version):
    if resource is None:
        return
    for k, v in resource.items():
        if isinstance(v, dict):
            set_model_version(v, model_version)
        elif isinstance(v, str):
            if k == "schema:schemaVersion":
                resource[k] = model_version


def setup_mongodb_client(mongodb_conn):
    if mongodb_conn is None:
        return None
    return MongoClient(mongodb_conn)


def setup_source_database(mongodb_client, source_db_name):
    if mongodb_client is None or source_db_name is None:
        return None

    db_names = mongodb_client.database_names()
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


def print_progressbar(resource_id, counter, total_count):
    resource_hash = extract_resource_hash(resource_id)
    percent = 100 * (counter / total_count)
    filled_length = int(percent)
    bar = "#" * filled_length + '-' * (100 - filled_length)
    print("Patching (%d/%d): |%s| %d%% Complete [%s]" % (counter, total_count, bar, percent, resource_hash), end='\r')


def get_template_ids(source_database, limit):
    template_ids = []
    if limit:
        found_ids = source_database['templates'].distinct("@id").limit(limit)
        template_ids.extend(found_ids)
    else:
        found_ids = source_database['templates'].distinct("@id")
        template_ids.extend(found_ids)
    filtered_ids = filter(lambda x: x is not None, template_ids)
    return list(filtered_ids)


def get_element_ids(source_database, limit):
    element_ids = []
    if limit:
        found_ids = source_database['template-elements'].distinct("@id").limit(limit)
        element_ids.extend(found_ids)
    else:
        found_ids = source_database['template-elements'].distinct("@id")
        element_ids.extend(found_ids)
    filtered_ids = filter(lambda x: x is not None, element_ids)
    return list(filtered_ids)


def get_instance_ids(source_database, limit):
    instance_ids = []
    if limit:
        found_ids = source_database['template-instances'].distinct("@id").limit(limit)
        instance_ids.extend(found_ids)
    else:
        found_ids = source_database['template-instances'].distinct("@id")
        instance_ids.extend(found_ids)
    filtered_ids = filter(lambda x: x is not None, instance_ids)
    return list(filtered_ids)


def read_list(filename):
    with open(filename) as infile:
        resource_ids = infile.readlines()
        return [id.strip() for id in resource_ids]


def read_json(filename):
    with open(filename) as infile:
        content = json.load(infile)
        return content


def get_template_from_mongodb(source_database, template_id):
    template = source_database['templates'].find_one({'@id': template_id})
    return post_read(template)


def get_element_from_mongodb(source_database, element_id):
    element = source_database['template-elements'].find_one({'@id': element_id})
    return post_read(element)


def get_instance_from_mongodb(source_database, instance_id):
    instance = source_database['template-instances'].find_one({'@id': instance_id})
    return post_read(instance)


def post_read(resource):
    new = {}
    for k, v in resource.items():
        if k == '_id':
            continue
        if isinstance(v, dict):
            v = post_read(v)
        new[k.replace('_$schema', '$schema')] = v
    return new


def extract_resource_hash(resource_id):
    return resource_id[resource_id.rfind('/')+1:]


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
