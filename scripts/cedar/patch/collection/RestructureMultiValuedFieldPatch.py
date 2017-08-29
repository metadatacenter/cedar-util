import jsonpatch
import re
import dpath
from cedar.patch import utils
from cedar.patch.collection import utils as cedar_helper


class RestructureMultiValuedFieldPatch(object):

    def __init__(self):
        self.description = "Restructure the model schema of a multi-valued field (i.e., checkbox and multi-select list)"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"
        self.path = None

    def is_applied(self, error_description, template=None):
        pattern = re.compile("object has missing required properties \(\['items','minItems'\]\) at (/properties/[^/]+)+")
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
            "op": "move",
            "from": self.path,
            "to": self.path + "/items"
        }
        patches.append(patch)

        patch = {
            "op": "add",
            "value": "array",
            "path": self.path + "/type"
        }
        patches.append(patch)

        patch = {
            "op": "add",
            "value": 1,
            "path": self.path + "/minItems"
        }
        patches.append(patch)

        return patches
