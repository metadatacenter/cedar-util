import jsonpatch
import re
from cedar.utils import general_utils as utils


class FillEmptyPropertyDescriptionPatch(object):

    def __init__(self):
        self.description = "Fills empty property description with a default string value"
        self.from_version = "1.3.0"
        self.to_version = "1.4.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "string '' is too short \(length: 0, required minimum: 1\) " \
            "at /_ui/propertyDescriptions/.*$")
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
            "value": "Help Text",
            "path": path
        }]
        return jsonpatch.JsonPatch(patches)
