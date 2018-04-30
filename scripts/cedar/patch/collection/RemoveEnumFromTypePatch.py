import jsonpatch
import re
from cedar.patch import utils


class RemoveEnumFromTypePatch(object):

    def __init__(self):
        self.description = "Fixes the schema definition of the @type object for a static template field"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: \['enum'\] " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties/@type$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        patches = [{
            "op": "remove",
            "path": path
        },
        {
            "op": "add",
            "value": {
                "type": "string",
                "format": "uri"
            },
            "path": path
        }]
        return jsonpatch.JsonPatch(patches)
