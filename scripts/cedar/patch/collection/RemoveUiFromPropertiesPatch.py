import jsonpatch
import re
from cedar.patch import utils


class RemoveUiFromPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the '_ui' field from the properties object"
        self.from_version = "1.2.0"
        self.to_version = "1.3.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: " \
            "\[('.+',)*'_ui'(,'.+')*\] " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        patches = [{
            "op": "remove",
            "path": path + "/_ui"
        }]
        return jsonpatch.JsonPatch(patches)
