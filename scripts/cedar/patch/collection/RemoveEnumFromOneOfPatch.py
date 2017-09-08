import jsonpatch
import re
from cedar.patch import utils


class RemoveEnumFromOneOfPatch(object):

    def __init__(self):
        self.description = "Fixes the schema definition of the @type object for the non-static template field"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile(
            "array is too long: must have at most 2 elements but instance has 3 elements at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties/@type/oneOf$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            return True
        else:
            return False

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
