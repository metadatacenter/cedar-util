import sys
import argparse
import os
import json
from pymongo import MongoClient
from requests import HTTPError
import cedar.utils.general_utils as utils
import cedar.constants as const

from cedar.patch.patches.UpdateSchemaVersion import UpdateSchemaVersion
from cedar.utils import validator, to_json_string, write_to_file, print_progressbar, extract_resource_hash
from cedar.patch.patches.AddMissingColonToDatetimePatch import AddMissingColonToDatetimePatch
from cedar.patch.patches.RestructureDateFieldPatch import RestructureDateFieldPatch
from cedar.patch.PatchingEngine import PatchingEngine

cedar_server_address = "https://resource." + os.environ['CEDAR_HOST']
cedar_api_key = "apiKey " + os.environ['CEDAR_ADMIN_USER_API_KEY']
mongodb_conn = "mongodb://" + os.environ['CEDAR_MONGO_ROOT_USER_NAME'] + ":" + os.environ['CEDAR_MONGO_ROOT_USER_PASSWORD'] + "@localhost:27017/admin"
report = {
    "resolved": [],
    "unresolved": [],
    "error": []
}


def main():

    print("Execution path: " + str(sys.path))

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type",
                        choices=['template', 'element', 'field', 'template-instance', 'all'],
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
        pass # TODO
        # if resource_type == 'template':
        #     template = read_json(input_file)
        #     patch_template_from_json(patch_engine, template, output_dir, debug)
        # elif resource_type == 'element':
        #     element = read_json(input_file)
        #     patch_element_from_json(patch_engine, element, output_dir, debug)
        # elif resource_type == 'field':
        #     field = read_json(input_file)
        #     patch_field_from_json(patch_engine, field, output_dir, debug)
    elif input_mongodb is not None:
        mongodb_client = setup_mongodb_client(mongodb_conn)
        source_database = setup_source_database(mongodb_client, input_mongodb)
        target_database = setup_target_database(mongodb_client, output_mongodb)
        if resource_type == 'template' or resource_type == 'all':
            template_ids = read_list(filter_list) if filter_list is not None else get_resource_ids(source_database, const.MONGODB_TEMPLATE_COLLECTION, limit)
            print("------------------------------------------------------------------------------")
            print("Patching templates from '" + input_mongodb + "' and saving them to '" + output_mongodb + "'")
            print("------------------------------------------------------------------------------")
            patch_resource(patch_engine, template_ids, source_database, output_dir, target_database, debug)
        if resource_type == 'element' or resource_type == 'all':
            print("------------------------------------------------------------------------------")
            print("Patching template elements from '" + input_mongodb + "' and saving them to '" + output_mongodb + "'")
            print("------------------------------------------------------------------------------")
            element_ids = read_list(filter_list) if filter_list is not None else get_resource_ids(source_database, const.MONGODB_TEMPLATE_ELEMENT_COLLECTION, limit)
            patch_resource(patch_engine, element_ids, source_database, output_dir, target_database, debug)
        if resource_type == 'field' or resource_type == 'all':
            print("------------------------------------------------------------------------------")
            print("Patching template fields from '" + input_mongodb + "' and saving them to '" + output_mongodb + "'")
            print("------------------------------------------------------------------------------")
            field_ids = read_list(filter_list) if filter_list is not None else get_resource_ids(source_database, const.MONGODB_TEMPLATE_FIELD_COLLECTION, limit)
            patch_resource(patch_engine, field_ids, source_database, output_dir, target_database, debug)
        if resource_type == 'template-instance' or resource_type == 'all':
            print("------------------------------------------------------------------------------")
            print("Patching template instances from '" + input_mongodb + "' and saving them to '" + output_mongodb + "'")
            print("------------------------------------------------------------------------------")
            instance_ids = read_list(filter_list) if filter_list is not None else get_resource_ids(source_database, const.MONGODB_TEMPLATE_INSTANCE_COLLECTION, limit)
            patch_resource(patch_engine, instance_ids, source_database, output_dir, target_database, debug)

    if not debug:
        show_report()


def build_patch_engine():
    return build_patch_engine_v150_to_v160()


def build_patch_engine_v150_to_v160():
    patch_engine = PatchingEngine()
    patch_engine.add_patch(RestructureDateFieldPatch())
    patch_engine.add_patch(AddMissingColonToDatetimePatch())
    patch_engine.add_patch(UpdateSchemaVersion(new_version="1.6.0"))
    return patch_engine


def patch_resource(patch_engine, resource_ids, source_database, output_dir=None, target_database=None, debug=False):
    for counter, resource_id in enumerate(resource_ids, start=1):
        print_progressbar(resource_id, counter, len(resource_ids), message="Patching")
        try:
            resource_type = utils.get_resource_type_from_id(resource_id)
            mongo_collection = utils.get_mongodb_collection_name_from_resource_type(resource_type)
            resource = read_from_mongodb(source_database, mongo_collection, resource_id)
            is_success, patched_resource = patch_engine.execute(resource, validate_resource_callback)

            print(resource_id)
            print(is_success)
            print(patched_resource)

            if is_success:
                if patched_resource is not None:
                    create_report("resolved", resource_id)
                    if output_dir is not None:
                        filename = create_filename_from_id(resource_id, prefix=resource_type + "-patched-")
                        write_to_file(patched_resource, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, mongo_collection, patched_resource)
                else:
                    if output_dir is not None:
                        filename = create_filename_from_id(resource_id, prefix=resource_type + "-")
                        write_to_file(resource, filename, output_dir)
                    if target_database is not None:
                        write_to_mongodb(target_database, mongo_collection, resource)
            else:
                create_report("unresolved", resource_id)
                if output_dir is not None:
                    if patched_resource is None:
                        patched_resource = resource
                    filename = create_filename_from_id(resource_id, prefix=resource_type +"-partially-patched-")
                    write_to_file(patched_resource, filename, output_dir)
                if target_database is not None:  # Save the original to the database
                    write_to_mongodb(target_database, mongo_collection, resource)
        except (HTTPError, KeyError) as error:
            create_report("error", [resource_id, "Error details: " + str(error)])
    print()  # console printing separator


def validate_resource_callback(resource):
    resource_type = utils.get_resource_type(resource)
    if resource_type == const.RESOURCE_TYPE_TEMPLATE:
        is_valid, message = validator.validate_template(cedar_server_address, cedar_api_key, resource)
    elif resource_type == const.RESOURCE_TYPE_TEMPLATE_ELEMENT:
        is_valid, message = validator.validate_element(cedar_server_address, cedar_api_key, resource)
    elif resource_type == const.RESOURCE_TYPE_TEMPLATE_FIELD:
        is_valid, message = validator.validate_field(cedar_server_address, cedar_api_key, resource)
    elif resource_type == const.RESOURCE_TYPE_TEMPLATE_INSTANCE:
        is_valid, message = validator.validate_instance(cedar_server_address, cedar_api_key, resource)

    return is_valid, [error_detail["message"] + " at " + error_detail["location"]
                      for error_detail in message["errors"]
                      if not is_valid]


# def patch_field_from_json(patch_engine, field, output_dir, debug):
#     try:
#         field_id = field["@id"]
#         is_success, patched_field = patch_engine.execute(field, validate_field_callback, debug=debug)
#         if is_success:
#             if patched_field is not None:
#                 create_report("resolved", field_id)
#                 if output_dir is not None:
#                     filename = create_filename_from_id(field_id, prefix="field-patched-")
#                     write_to_file(patched_field, filename, output_dir)
#         else:
#             create_report("unresolved", field_id)
#             if output_dir is not None:
#                 filename = create_filename_from_id(field_id, prefix="field-partially-patched-")
#                 write_to_file(patched_field, filename, output_dir)
#     except (HTTPError, KeyError, TypeError) as error:
#         create_report("error", [field_id, "Error details: " + str(error)])


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

    db_names = mongodb_client.list_database_names()
    if output_mongodb in db_names:
        print("Existing databases: " + str(db_names))
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
        found_id_objs = database[collection_name].find({}, {"@id": 1})
    else:
        found_id_objs = database[collection_name].find({}, {"@id": 1})

    for found_id_obj in found_id_objs:
        resource_id = found_id_obj['@id']
        if resource_id is not None:
            resource_ids.append(resource_id)
    # remove duplicates
    resource_ids = list(dict.fromkeys(resource_ids))
    return resource_ids


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
