import jsonpatch
import re
from cedar.patch import utils


class RemoveEnumFromOneOfPatch(object):

    def __init__(self):
        self.description = "Fixes the schema definition of the @type object for the non-static template field"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "array is too long: must have at most 2 elements but instance has 3 elements " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties/@type/oneOf$")
        return pattern.match(error_message)

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(doc, error):
        error_description = error
        path = utils.get_error_location(error_description)
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
