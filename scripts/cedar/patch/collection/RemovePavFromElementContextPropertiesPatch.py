import jsonpatch
import re
from cedar.patch import utils


class RemovePavFromElementContextPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the 'pav' prefix in the @context/properties object of an element"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: " \
            "\[('.+',)*'pav'(,'.+')*\] " \
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
            "path": path + "/pav"
        },
        {
            "op": "replace",
            "value": [item for item in required_list if item != "pav"],
            "path": parent_path + "/required"
        }]
        return jsonpatch.JsonPatch(patches)