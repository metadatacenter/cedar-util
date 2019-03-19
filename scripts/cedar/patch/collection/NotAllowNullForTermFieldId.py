import jsonpatch
import re
from cedar.patch import utils


class NotAllowNullForTermFieldId(object):

    def __init__(self):
        self.description = "Removes the option to have a 'null' value in the @id field of a controlled-term field"
        self.from_version = "1.5.0"
        self.to_version = "1.6.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance failed to match exactly one schema \(matched 0 out of 6\) " \
            "at .*$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        if utils.path_exists(doc, path + "/properties"):
            patches = [{
                "op": "replace",
                "value": "string",
                "path": path + "/properties/@id/type"
            }]
        else:
            patches = [{
                "op": "replace",
                "value": "string",
                "path": path + "/items/properties/@id/type"
            }]
        return jsonpatch.JsonPatch(patches)