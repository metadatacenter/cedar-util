import argparse
import os
import re
from requests import HTTPError
from cedar.patch.utils import is_template_field, is_static_template_field
from cedar.utils import print_progressbar, searcher
from pymongo import MongoClient



cedar_template_collection = "templates"
cedar_element_collection = "template-elements"

ignoreList = ["@id", "@type", "@value", "@context", "_$schema", "_ui", "oslc:modifiedBy",
               "pav:createdBy", "pav:createdOn", "pav:lastUpdatedOn", "bibo:status",
               "rdfs:label", "skos:notation", "schema:name", "schema:description",
               "schema:isBasedOn", "schema:schemaVersion", "required", "type",
               "additionalProperties", "skos", "xsd", "pav", "schema", "oslc", "rdfs"]

cedar_server_address = "https://resource." + os.environ['CEDAR_HOST']
cedar_api_key = "apiKey " + os.environ['CEDAR_ADMIN_USER_API_KEY']
mongodb_conn = "mongodb://" + os.environ['CEDAR_MONGO_ROOT_USER_NAME'] + ":" + os.environ['CEDAR_MONGO_ROOT_USER_PASSWORD'] + "@localhost:27017/admin"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type",
                        choices=['template', 'element'],
                        help="the type of CEDAR resource")
    parser.add_argument("--input-mongodb",
                        required=False,
                        metavar="DBNAME",
                        help="set the MongoDB database where resources are located")

    args = parser.parse_args()
    resource_type = args.type
    cedar_database = args.input_mongodb

    mongodb_client = MongoClient(mongodb_conn)
    database = mongodb_client[cedar_database]
    if resource_type == 'template':
        template_ids = get_resource_ids(database, cedar_template_collection)
        patch_uuid_in_templates(template_ids, database)
    elif resource_type == 'element':
        element_ids = get_resource_ids(database, cedar_element_collection)
        patch_uuid_in_elements(element_ids, database)
    elif resource_type == 'field':
        print("Feature not supported")


def patch_uuid_in_templates(template_ids, database):
    patched_templates = []
    total_templates = len(template_ids)
    for counter, template_id in enumerate(template_ids, start=1):
        try:
            print_progressbar(template_id, counter, total_templates, message="Checking")
            if not has_instances(template_id):
                template = read_from_mongodb(database, cedar_template_collection, template_id)
                if contains_uuid(template):
                    patched_template = patch_uuid(template)
                    patched_templates.append(template_id)
                    write_to_mongodb(database, cedar_template_collection, patched_template)
        except (HTTPError, KeyError) as error:
            pass
    print(len(patched_templates), "templates were successfully patched.")


def patch_uuid_in_elements(element_ids, database):
    patched_elements = []
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        try:
            print_progressbar(element_id, counter, total_elements, message="Checking")
            element = read_from_mongodb(database, cedar_element_collection, element_id)
            if contains_uuid(element):
                patched_element = patch_uuid(element)
                patched_elements.append(element_id)
                write_to_mongodb(database, cedar_element_collection, patched_element)
        except KeyError as error:
            pass
    print(len(patched_elements), "elements were successfully patched.")


def has_instances(template_id):
    instances = searcher.search_instances_of(cedar_server_address, cedar_api_key, template_id)
    return len(instances) > 0


def contains_uuid(obj):
    uuid_names = []
    check_recursively(obj, uuid_names)
    return len(uuid_names) > 0


def check_recursively(obj, uuid_names):
    if obj is None:
        return
    for k, v in obj.items():
        if is_uuid(k):
            uuid_names.append(k)
        if isinstance(v, dict):
            check_recursively(v, uuid_names)


def patch_uuid(resource):
    patch_recursively(resource)
    return resource


def patch_recursively(resource):
    if resource is None:
        return

    if "items" in resource:
        resource = resource["items"]

    if is_template_field(resource) or is_static_template_field(resource):
        return

    # Remove field names in "@context", "required" and "_ui" that are
    # not listed in the template's or element's "properties"
    propertiesList = [x for x in resource["properties"].keys() if x not in ignoreList]
    contextList = [x for x in resource["properties"]["@context"]["properties"].keys() if x not in ignoreList]
    removeList = [x for x in contextList if x not in propertiesList]
    for fieldName in removeList:
        del resource["properties"]["@context"]["properties"][fieldName]
        if fieldName in resource["required"]:
            resource["required"].remove(fieldName)
        if fieldName in resource["properties"]["@context"]["required"]:
            resource["properties"]["@context"]["required"].remove(fieldName)
        if "order" in resource["_ui"] and fieldName in resource["_ui"]["order"]:
            resource["_ui"]["order"].remove(fieldName)
        if "propertyLabels" in resource["_ui"] and fieldName in resource["_ui"]["propertyLabels"]:
            del resource["_ui"]["propertyLabels"][fieldName]
        if "propertyDescriptions" in resource["_ui"] and fieldName in resource["_ui"]["propertyDescriptions"]:
            del resource["_ui"]["propertyDescriptions"][fieldName]

    # Rename all UUID fields that occur in "@context", "required", "_ui"
    # with a proper name found in the "schema:name" field
    for fieldName in propertiesList:
        if is_uuid(fieldName):
            if "items" in resource["properties"][fieldName]:
                newName = resource["properties"][fieldName]["items"]["schema:name"]
            else:
                newName = resource["properties"][fieldName]["schema:name"]
            resource["properties"][newName] = resource["properties"].pop(fieldName)
            if fieldName in resource["properties"]["@context"]["properties"]:
                resource["properties"]["@context"]["properties"][newName] = resource["properties"]["@context"][
                    "properties"].pop(fieldName)
            if fieldName in resource["required"]:
                resource["required"].remove(fieldName)
                resource["required"].append(newName)
            if fieldName in resource["properties"]["@context"]["required"]:
                resource["properties"]["@context"]["required"].remove(fieldName)
                resource["properties"]["@context"]["required"].append(newName)
            if  "order" in resource["_ui"] and fieldName in resource["_ui"]["order"]:
                resource["_ui"]["order"].remove(fieldName)
                resource["_ui"]["order"].append(newName)
            if "propertyLabels" in resource["_ui"] and fieldName in resource["_ui"]["propertyLabels"]:
                del resource["_ui"]["propertyLabels"][fieldName]
                resource["_ui"]["propertyLabels"][newName] = newName
            if "propertyDescriptions" in resource["_ui"] and fieldName in resource["_ui"]["propertyDescriptions"]:
                resource["_ui"]["propertyDescriptions"][newName] = resource["_ui"]["propertyDescriptions"].pop(fieldName)

    propertiesList = [x for x in resource["properties"].keys() if x not in ignoreList]
    for fieldName in propertiesList:
        innerResource = resource["properties"][fieldName]
        patch_recursively(innerResource)


def get_resource_ids(database, collection_name):
    resource_ids = []
    found_ids = database[collection_name].distinct("@id")
    resource_ids.extend(found_ids)
    filtered_ids = filter(lambda x: x is not None, resource_ids)
    return list(filtered_ids)


def read_from_mongodb(database, collection_name, resource_id):
    return database[collection_name].find_one({'@id': resource_id})


def write_to_mongodb(database, collection_name, resource):
    database[collection_name].replace_one({'@id': resource['@id']}, resource)


def is_uuid(uuid):
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    match = regex.match(uuid)
    return bool(match)


if __name__ == "__main__":
    main()
