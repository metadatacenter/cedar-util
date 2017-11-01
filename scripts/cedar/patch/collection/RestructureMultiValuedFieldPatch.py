import jsonpatch
import re
import dpath
from cedar.patch import utils


class RestructureMultiValuedFieldPatch(object):

    def __init__(self):
        self.description = "Restructure the model schema of a multi-valued field (i.e., checkbox and multi-select list)"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object has missing required properties \(\['items','minItems'\]\) " \
            "at (/properties/[^/]+)+")
        is_applied = False
        if pattern.match(error_message):
            path = utils.get_error_location(error_message)
            if utils.is_multivalued_field(doc, at=path):
                is_applied = True
        return is_applied

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        property_object = utils.get_json_object(doc, path)

        patches = [{
            "op": "remove",
            "path": path
        },
        {
            "op": "add",
            "value": {},
            "path": path
        },
        {
            "op": "add",
            "value": "array",
            "path": path + "/type"
        },
        {
            "op": "add",
            "value": 1,
            "path": path + "/minItems"
        },
        {
            "op": "add",
            "value": property_object,
            "path": path + "/items"
        }]
        return jsonpatch.JsonPatch(patches)
