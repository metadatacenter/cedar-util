import os
import argparse
import dpath.util
from pymongo import MongoClient

mongodb_user = os.environ['CEDAR_MONGO_ROOT_USER_NAME']
mongodb_pass = os.environ['CEDAR_MONGO_ROOT_USER_PASSWORD']
mongodb_conn = "mongodb://" + mongodb_user + ":" + mongodb_pass + "@localhost:27017/admin"
db_name = "cedar"

cedar_template_collection = "templates"
cedar_element_collection = "template-elements"
cedar_field_collection = "template-fields"

cedar_template_element_iri = "https://schema.metadatacenter.org/core/TemplateElement"
cedar_template_field_iri = "https://schema.metadatacenter.org/core/TemplateField"

# The patch variables
skos_prefix = "skos"
skos_value = "http://www.w3.org/2004/02/skos/core#"

skos_preflabel = "skos:prefLabel"
skos_preflabel_def = { "@type": "xsd:string" }

skos_altlabel = "skos:altLabel"
skos_altlabel_def = { "@type": "xsd:string" }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type",
                        choices=['template', 'element', 'field'],
                        default="template",
                        help="the type of CEDAR resource")
    args = parser.parse_args()
    resource_type = args.type

    mongodb_client = MongoClient(mongodb_conn)
    mongodb_db = mongodb_client[db_name]

    if resource_type == 'template':
        mongodb_templates_collection = mongodb_db[cedar_template_collection]
        perform_patching(mongodb_templates_collection)
    elif resource_type == 'element':
        mongodb_elements_collection = mongodb_db[cedar_element_collection]
        perform_patching(mongodb_elements_collection)
    elif resource_type == 'field':
        pass


def perform_patching(mongodb_collection):
    for resource in mongodb_collection.find():
        path_list = []
        try:
            resource_id = resource["@id"]
            print("Patching " + resource_id)
            traverse_and_collect_field_paths(resource, [], path_list)
            for path in path_list:
                add_skos_prefix(resource, path)
                add_skos_prefLabel(resource, path)
                add_skos_altLabel(resource, path)
            write_to_mongodb(mongodb_collection, resource)
        except KeyError:
            continue
    print("Done.")


def add_skos_prefix(resource, field_path):
    skos_context_path = field_path.copy()
    skos_context_path.append("@context")
    skos_context_path.append(skos_prefix)
    dpath.util.new(resource, skos_context_path, skos_value)


def add_skos_prefLabel(resource, field_path):
    skos_preflabel_context_path = field_path.copy()
    skos_preflabel_context_path.append("@context")
    skos_preflabel_context_path.append(skos_preflabel)
    dpath.util.new(resource, skos_preflabel_context_path, skos_preflabel_def)


def add_skos_altLabel(resource, field_path):
    skos_altlabel_context_path = field_path.copy()
    skos_altlabel_context_path.append("@context")
    skos_altlabel_context_path.append(skos_altlabel)
    dpath.util.new(resource, skos_altlabel_context_path, skos_altlabel_def)


def write_to_mongodb(mongodb_collection, resource):
    resource_id = resource['@id']
    mongodb_collection.replace_one({'@id': resource_id}, resource)


def traverse_and_collect_field_paths(doc, parent_path, path_list):
    properties = doc['properties']
    if properties:
        for key in properties:
            property_object = properties[key]
            if is_single_element(property_object):
                new_parent_path = parent_path.copy()
                new_parent_path.append("properties")
                new_parent_path.append(key)
                traverse_and_collect_field_paths(property_object, new_parent_path, path_list)
            elif is_single_field(property_object):
                field_path = parent_path.copy()
                field_path.append("properties")
                field_path.append(key)
                path_list.append(field_path)
            elif is_multiple_element(property_object):
                new_parent_path = parent_path.copy()
                new_parent_path.append("properties")
                new_parent_path.append(key)
                new_parent_path.append("items")
                element = property_object['items']
                traverse_and_collect_field_paths(element, new_parent_path, path_list)
            elif is_multiple_field(property_object):
                field_path = parent_path.copy()
                field_path.append("properties")
                field_path.append(key)
                field_path.append("items")
                path_list.append(field_path)


def is_single_element(doc):
    return is_element(doc)


def is_element(doc):
    try:
        resource_type = doc['@type']
        return resource_type and resource_type == cedar_template_element_iri
    except KeyError:
        return False


def is_single_field(doc):
    return is_field(doc)


def is_field(doc):
    try:
        resource_type = doc['@type']
        return resource_type and resource_type == cedar_template_field_iri
    except KeyError:
        return False


def is_multiple_element(doc):
    try:
        item = doc['items']
        return item and is_element(item)
    except KeyError:
        return False


def is_multiple_field(doc):
    try:
        item = doc['items']
        return item and is_field(item)
    except KeyError:
        return False


if __name__ == "__main__":
    main()