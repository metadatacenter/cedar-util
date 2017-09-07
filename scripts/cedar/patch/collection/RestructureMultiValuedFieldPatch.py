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

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=True)

        error_description = error
        is_applied = False
        pattern = re.compile("object has missing required properties \(\['items','minItems'\]\) at (/properties/[^/]+)+")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            resource_obj = dpath.util.get(doc, self.path)
            if cedar_helper.is_multivalued_field(resource_obj):
                is_applied = True
        return is_applied

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc=None, path=None):
        utils.check_argument('doc', doc, isreq=True)
        utils.check_argument('path', path, isreq=False)

        element_or_field = dpath.util.get(doc, self.path)

        patches = []
        patch = {
            "op": "remove",
            "path": self.path
        }
        patches.append(patch)

        patch = {
            "op": "add",
            "value": {},
            "path": self.path
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

        patch = {
            "op": "add",
            "value": element_or_field,
            "path": self.path + "/items"
        }
        patches.append(patch)

        return patches
