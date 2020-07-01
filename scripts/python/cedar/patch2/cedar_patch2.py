import sys
import argparse
import json
from pymongo import MongoClient
from requests import HTTPError
import cedar.patch2.constants as const

from cedar.patch2.patches.update_schema_version_patch import UpdateSchemaVersion
import cedar.utils.general_utils as util
from cedar.utils import validator
from cedar.patch2.patches.add_missing_colon_to_datetime_patch import AddMissingColonToDatetimePatch
from cedar.patch2.patches.restructure_date_field_patch import RestructureDateFieldPatch
from cedar.patch2.patch_engine import PatchingEngine

report = {
    "resolved": [],
    "unresolved": [],
    "error": []
}


def main():

    print("Execution path: " + str(sys.path))

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--resource-type",
                        choices=['templates', 'elements', 'fields', 'instances', 'all'],
                        default="template",
                        help="the type of CEDAR resource")
    parser.add_argument("-i", "--input-mongodb",
                        required=True,
                        default="cedar",
                        metavar="INPUT_DB",
                        help="set the MongoDB database where resources are located")
    parser.add_argument("-o", "--output-mongodb",
                        required=True,
                        metavar="OUTPUT_DB",
                        help="set the MongoDB database name to store the patched resources")
    parser.add_argument("-l", "--limit",
                        required=False,
                        type=int,
                        help="the maximum number of resources to patch")

    args = parser.parse_args()
    resource_type = args.resource_type
    input_mongodb = args.input_mongodb
    limit = args.limit
    output_mongodb = args.output_mongodb

    patch_engine = build_patch_engine()

    if input_mongodb is not None and output_mongodb is not None:
        mongodb_client = setup_mongodb_client(const.MONGODB_CONNECTION_STRING)
        source_database = setup_source_database(mongodb_client, input_mongodb)
        target_database = setup_target_database(mongodb_client, output_mongodb)
        if resource_type == 'templates' or resource_type == 'all':
            template_ids = get_resource_ids(source_database, const.MONGODB_TEMPLATE_COLLECTION, limit)
            print('Patching ' + str(len(template_ids)) + ' Templates:')
            patch_resources(patch_engine, template_ids, source_database, target_database)
        if resource_type == 'elements' or resource_type == 'all':
            element_ids = get_resource_ids(source_database, const.MONGODB_TEMPLATE_ELEMENT_COLLECTION, limit)
            print('Patching ' + str(len(element_ids)) + ' Elements:')
            patch_resources(patch_engine, element_ids, source_database, target_database)
        if resource_type == 'fields' or resource_type == 'all':
            field_ids = get_resource_ids(source_database, const.MONGODB_TEMPLATE_FIELD_COLLECTION, limit)
            print('Patching ' + str(len(field_ids)) + ' Fields:')
            patch_resources(patch_engine, field_ids, source_database, target_database)
        if resource_type == 'instances' or resource_type == 'all':
            instance_ids = get_resource_ids(source_database, const.MONGODB_TEMPLATE_INSTANCE_COLLECTION, limit)
            print('Patching ' + str(len(instance_ids)) + ' Instances:')
            patch_resources(patch_engine, instance_ids, source_database, target_database)
    show_report()


def build_patch_engine():
    return build_patch_engine_v150_to_v160()


def build_patch_engine_v150_to_v160():
    patch_engine = PatchingEngine()
    patch_engine.add_patch(RestructureDateFieldPatch())
    patch_engine.add_patch(AddMissingColonToDatetimePatch())
    patch_engine.add_patch(UpdateSchemaVersion(new_version="1.6.0"))
    return patch_engine


def patch_resources(patch_engine, resource_ids, source_database, target_database):
    for counter, resource_id in enumerate(resource_ids, start=1):
        util.print_progressbar(resource_id, counter, len(resource_ids), message="Patching")
        try:
            resource_type = util.get_resource_type_from_id(resource_id)
            print('Patching ' + resource_type + ": " + resource_id)
            mongo_collection = util.get_mongodb_collection_name_from_resource_type(resource_type)
            resource = read_from_mongodb(source_database, mongo_collection, resource_id)
            is_success, patched_resource = patch_engine.execute(resource, validate_resource_callback)

            if is_success:
                if patched_resource is not None:
                    create_report("resolved", resource_id)
                    if target_database is not None:
                        write_to_mongodb(target_database, mongo_collection, patched_resource)
                else:
                    if target_database is not None:
                        write_to_mongodb(target_database, mongo_collection, resource)
            else:
                create_report("unresolved", resource_id)
                if target_database is not None:  # Save the original to the database
                    write_to_mongodb(target_database, mongo_collection, resource)
        except (HTTPError, KeyError) as error:
            create_report("error", [resource_id, "Error details: " + str(error)])
    print()  # console printing separator


def validate_resource_callback(resource):
    resource_type = util.get_resource_type(resource)
    if resource_type == const.RESOURCE_TYPE_TEMPLATE:
        is_valid, message = validator.validate_template(const.CEDAR_SERVER_ADDRESS, const.CEDAR_ADMIN_API_KEY, resource)
    elif resource_type == const.RESOURCE_TYPE_TEMPLATE_ELEMENT:
        is_valid, message = validator.validate_element(const.CEDAR_SERVER_ADDRESS, const.CEDAR_ADMIN_API_KEY, resource)
    elif resource_type == const.RESOURCE_TYPE_TEMPLATE_FIELD:
        is_valid, message = validator.validate_field(const.CEDAR_SERVER_ADDRESS, const.CEDAR_ADMIN_API_KEY, resource)
    elif resource_type == const.RESOURCE_TYPE_TEMPLATE_INSTANCE:
        is_valid, message = validator.validate_instance(const.CEDAR_SERVER_ADDRESS, const.CEDAR_ADMIN_API_KEY, resource)

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

    db_names = mongodb_client.list_database_names()
    if output_mongodb in db_names:
        print("Existing databases: " + str(db_names))
        if confirm("The patch database '" + output_mongodb + "' already exists. Drop the content to proceed (Y/[N])?", default_response=False):
            print("Dropping '" + output_mongodb + "' database...")
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
    resource_hash = util.extract_resource_hash(resource_id)
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
    print('EXECUTION SUMMARY: ')
    print('- Patched and valid: ' + str(len(report["resolved"])))
    print('- Patched but invalid: ' + str(len(report["unresolved"])))
    if len(report["unresolved"]) > 0:
        for unresolved_id in report["unresolved"]:
            print('    - ' + unresolved_id)
    print('- Errored during patching: ' + str(len(report["error"])))
    if len(report["error"]) > 0:
        for errored_id in report["error"]:
            print('    - ' + errored_id)


# def create_report_message(solved_size, unsolved_size, error_size):
#     report_message = ""
#     if unsolved_size == 0 and error_size == 0:
#         report_message = "All resources were successfully patched."
#     else:
#         if solved_size == 0:
#             report_message = "Unable to completely fix the invalid resources"
#         else:
#             total_size = solved_size + unsolved_size + error_size
#             report_message += "Successfully fix %d out of %d invalid resources. (Success rate: %.0f%%)" % \
#                               (solved_size, total_size, solved_size * 100 / total_size)
#         report_message += "\n"
#         report_message += "Details: " + util.to_json_string(dict(report))
#     return report_message


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
