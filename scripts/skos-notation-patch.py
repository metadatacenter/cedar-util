import os
import jsonpatch
from pymongo import MongoClient

mongodb_user = os.environ['CEDAR_MONGO_ROOT_USER_NAME']
mongodb_pass = os.environ['CEDAR_MONGO_ROOT_USER_PASSWORD']
mongodb_conn = "mongodb://" + mongodb_user + ":" + mongodb_pass + "@localhost:27017/admin"
db_name = "cedar"

cedar_template_collection = "templates"

# The patch objects
skos_patch = [
    {
        "op": "add",
        "value": {
            "type": "string",
            "format": "uri",
            "enum": [
                "http://www.w3.org/2004/02/skos/core#"
            ]
        },
        "path": "/properties/@context/properties/skos"
    },
    {
        "op": "add",
        "value": "skos",
        "path": "/properties/@context/required/-"
    }]

skos_notation_patch = [
    {
        "op": "add",
        "value": {
            "type": "object",
            "properties": {
                "@type": {
                    "type": "string",
                    "enum": [
                        "xsd:string"
                    ]
                }
            }
        },
        "path": "/properties/@context/properties/skos:notation"
    },
    {
        "op": "add",
        "value": "skos:notation",
        "path": "/properties/@context/required/-"
    }]


def main():
    mongodb_client = MongoClient(mongodb_conn)
    mongodb_db = mongodb_client[db_name]
    mongodb_templates_collection = mongodb_db[cedar_template_collection]
    perform_patching(mongodb_templates_collection)


def perform_patching(templates_collection):
    was_invalid = False
    for template in templates_collection.find():
        try:
            template_id = template["@id"]
            print("Patching " + template_id)
            if not has_skos(template):
                template = jsonpatch.JsonPatch(skos_patch).apply(template)
                was_invalid = True
            if not has_skos_notation(template):
                template = jsonpatch.JsonPatch(skos_notation_patch).apply(template)
                was_invalid = True
            if was_invalid:
                write_to_mongodb(templates_collection, template)
                was_invalid = False
        except KeyError:
            continue
    print("Done.")


def has_skos(template):
    return 'skos' in template['properties']['@context']['properties']


def has_skos_notation(template):
    return 'skos:notation' in template['properties']['@context']['properties']


def write_to_mongodb(templates_collection, template):
    template_id = template['@id']
    templates_collection.replace_one({'@id': template_id}, template)


if __name__ == "__main__":
    main()