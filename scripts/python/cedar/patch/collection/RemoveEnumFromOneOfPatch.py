import jsonpatch
import re
from cedar.utils import general_utils as utils


class RemoveEnumFromOneOfPatch(object):

    def __init__(self):
        self.description = "Fixes the schema definition of the @type object for the non-static template field"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "array is too long: must have at most 2 elements but instance has 3 elements " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties/@type/oneOf$")
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
            "value": [
                {
                    "type": "string",
                    "format": "uri"
                },
                {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string",
                        "format": "uri"
                    },
                    "uniqueItems": True
                }
            ],
            "path": path
        }]
        return jsonpatch.JsonPatch(patches)
