import jsonpatch
import re
from cedar.patch import utils


class RemoveSchemaIsBasedOnFromPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the schema:isBasedOn in the properties of a template field or element"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: " \
            "\[('.+',)*'schema:isBasedOn'(,'.+')*\] " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties$")
        return pattern.match(error_message)

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(doc, error):
        utils.check_argument_not_none("doc", doc)
        utils.check_argument_not_none("error", error)

        error_description = error
        path = utils.get_error_location(error_description)

        parent_object, parent_path = utils.get_parent_object(doc, path)
        required_list = parent_object.get("required")

        patches = [{
            "op": "remove",
            "path": path + "/schema:isBasedOn"
        },
        {
            "op": "replace",
            "value": [item for item in required_list if item != "schema:isBasedOn"],
            "path": parent_path + "/required"
        }]
        return jsonpatch.JsonPatch(patches)
