import jsonpatch
import re
from cedar.patch import utils


class RemoveEnumFromOneOfPatch(object):

    def __init__(self):
        self.description = "Fixes the schema definition of the @type object for the non-static template field"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error_description, template=None):
        if template is None:
            pass # Just ignore

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

    def get_json_patch(self, doc=None, path=None):
        if doc is None:
            pass # Just ignore

        if self.path is None and path is None:
            raise Exception("The method requires the 'path' argument")

        if path is not None:
            self.path = path

        patches = []
        patch = {
            "op": "remove",
            "path": self.path
        }
        patches.append(patch)
        patch = {
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
            "path": self.path
        }
        patches.append(patch)

        return patches
