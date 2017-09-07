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
        utils.check_argument_not_none(template, "The method requires the 'template' argument")

        is_applied = False
        pattern = re.compile("object has missing required properties \(\['items','minItems'\]\) at (/properties/[^/]+)+")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            resource_obj = dpath.util.get(template, self.path)
            if cedar_helper.is_multivalued_field(resource_obj):
                is_applied = True
        return is_applied

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc=None, path=None):
        utils.check_argument_not_none(doc, "The method requires the 'doc' argument")

        if self.path is None and path is None:
            raise Exception("The method requires the 'path' argument")

        if path is not None:
            self.path = path

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
