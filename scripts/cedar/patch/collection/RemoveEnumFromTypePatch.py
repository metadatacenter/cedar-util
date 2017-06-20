import jsonpatch
import re
from cedar.patch import utils


class RemoveEnumFromTypePatch(object):

    def __init__(self):
        self.description = "Fixes the schema definition of the @type object for a static template field"
        self.since = "1.1.0"
        self.path = None

    def is_applied(self, error_description):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: \['enum'\] at (/properties/[^/]+)*/properties/@type$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc, path=None):
        if self.path is None and path is None:
            raise Exception("The method required a 'path' location")

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
            "value": {
                "type": "string",
                "format": "uri"
            },
            "path": self.path
        }
        patches.append(patch)

        return patches
