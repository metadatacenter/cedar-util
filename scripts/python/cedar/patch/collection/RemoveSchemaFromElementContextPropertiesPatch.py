import jsonpatch
import re
from cedar.utils import general_utils as utils


class RemoveSchemaFromElementContextPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the 'schema' prefix in the @context/properties object of an element"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: " \
            "\[('.+',)*'schema'(,'.+')*\] " \
            "at ((/properties/[^/@]+/items)*(/properties/[^/@]+)*)*/properties/@context/properties$")
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
            "path": path + "/schema"
        },
        {
            "op": "replace",
            "value": [item for item in required_list if item != "schema"],
            "path": parent_path + "/required"
        }]
        return jsonpatch.JsonPatch(patches)
