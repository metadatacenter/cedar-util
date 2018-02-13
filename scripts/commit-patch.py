import argparse
import json
from pymongo import MongoClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type",
                        choices=['template', 'element'],
                        default="template",
                        help="the type of CEDAR resource")
    parser.add_argument("--patch-dir",
                        required=False,
                        metavar="DIRNAME",
                        help="set the input directory of the patched resources")
    parser.add_argument("--lookup",
                        required=False,
                        metavar="FILENAME",
                        help="an input file containing a list of patched resource identifiers")
    parser.add_argument("--mongodb-connection",
                        required=False,
                        metavar="DBCONN",
                        help="set the MongoDB admin connection URI to perform administration operations")
    parser.add_argument("--input-mongodb",
                        required=False,
                        default="cedar",
                        metavar="DBNAME",
                        help="set the MongoDB database name to get the resources to validate")
    args = parser.parse_args()
    resource_type = args.type
    patch_dir = args.patch_dir
    patch_list = get_ids_from_file(args.lookup)

    mongodb_conn = args.mongodb_connection
    source_db_name = args.input_mongodb

    mongodb_client = setup_mongodb_client(mongodb_conn)
    source_database = setup_source_database(mongodb_client, source_db_name)

    if resource_type == 'template':
        commit_template_patch(patch_list, patch_dir, source_database)
    elif resource_type == 'element':
        commit_element_patch(patch_list, patch_dir, source_database)


def commit_template_patch(patch_list, patch_dir, source_database):
    for template_id in patch_list:
        patch_file = get_patch_file(patch_dir, template_id)
        print("Commit the patch: " + patch_file + "\r", end="")
        patched_template = read_file(patch_file)
        try:
            mongodb_index_id = get_mongodb_index_id(source_database, "templates", template_id)
            patched_template["_id"] = mongodb_index_id
            write_to_mongodb(source_database, "templates", patched_template)
            print("Commit the patch: " + patch_file + " - Success")
        except ValueError as error:
            print("Commit the patch: " + patch_file + " - Failed")
            print(str(error))
    print("Done.")


def commit_element_patch(patch_list, patch_dir, source_database):
    for element_id in patch_list:
        patch_file = get_patch_file(patch_dir, element_id)
        print("Commit the patch: " + patch_file + "\r", end="")
        patched_element = read_file(patch_file)
        try:
            mongodb_index_id = get_mongodb_index_id(source_database, "template-elements", element_id)
            patched_element["_id"] = mongodb_index_id
            write_to_mongodb(source_database, "template-elements", patched_element)
        except ValueError as error:
            print("Commit the patch: " + patch_file + " - Failed")
            print(str(error))
    print("Done.")


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


def get_mongodb_index_id(database, collection_name, resource_id):
    template = database[collection_name].find_one({'@id': resource_id})
    if template is None:
        raise ValueError("Resource ID not found")
    return template["_id"]


def write_to_mongodb(database, collection_name, patched_resource):
    database[collection_name].replace_one({'@id': patched_resource['@id']}, pre_write(patched_resource))


def pre_write(resource):
    new = {}
    for k, v in resource.items():
        if isinstance(v, dict):
            v = pre_write(v)
        new[k.replace('$schema', '_$schema')] = v
    return new


def get_ids_from_file(filename):
    with open(filename) as infile:
        resource_ids = infile.readlines()
        return [id.strip() for id in resource_ids]


def read_file(filename):
    with open(filename) as infile:
        content = json.load(infile)
        return content


def get_patch_file(patch_dir, resource_id):
    return patch_dir + "/" + extract_resource_hash(resource_id) + ".json"


def extract_resource_hash(resource_id):
    return resource_id[resource_id.rfind('/')+1:]


if __name__ == "__main__":
    main()
