import jsonpatch
import re
from cedar.utils import general_utils as utils


class FillNullValuePatch(object):

    def __init__(self):
        self.description = "Fills invalid null fields with a default 'blank' string value"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance type \(null\) does not match any allowed primitive type \(allowed: \['string'\]\) " \
            "at /.*$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        patches = [{
            "op": "add",
            "value": "blank",
            "path": path
        }]
        return jsonpatch.JsonPatch(patches)
