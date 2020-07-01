import jsonpatch
import re
from python.cedar.patch import utils


class AddValueConstraintsToFieldOrElementPatch(object):

    def __init__(self):
        self.description = "Adds the missing _valueConstraints in a template element or field"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'_valueConstraints'(,'.+')*\]\) " \
            "at ((/properties/[^/]+/items)*(/properties/[^/@]+)*)*$")
        is_applied = False
        if pattern.match(error_message):
            path = utils.get_error_location(error_message)
            if utils.is_template_element(doc, at=path) or utils.is_template_field(doc, at=path):
                is_applied = True
        return is_applied

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        patches = [{
            "op": "add",
            "value": {
                "requiredValue": False
            },
            "path": path + "/_valueConstraints"
        }]
        return jsonpatch.JsonPatch(patches)
