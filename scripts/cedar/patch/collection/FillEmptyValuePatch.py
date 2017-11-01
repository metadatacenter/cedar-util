import jsonpatch
import re
from cedar.patch import utils


class FillEmptyValuePatch(object):

    def __init__(self):
        self.description = "Fills empty fields with a default 'blank' string value"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "string '' is too short \(length: 0, required minimum: 1\) " \
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
