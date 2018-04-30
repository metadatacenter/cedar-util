import jsonpatch
import re
from cedar.patch import utils


class RemoveSchemaNameFromPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the schema:name in the properties of a template field or element"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: " \
            "\[('.+',)*'schema:name'(,'.+')*\] " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        parent_object, parent_path = utils.get_parent_object(doc, path)
        required_list = parent_object.get("required")

        patches = [{
            "op": "remove",
            "path": path + "/schema:name"
        },
        {
            "op": "replace",
            "value": [item for item in required_list if item != "schema:name"],
            "path": parent_path + "/required"
        }]
        return jsonpatch.JsonPatch(patches)
