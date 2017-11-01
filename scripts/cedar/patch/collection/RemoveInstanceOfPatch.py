import jsonpatch
import re
from cedar.patch import utils


class RemoveInstanceOfPatch(object):

    def __init__(self):
        self.description = "Removes the invalid 'instanceOf:' field"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: \['instanceOf:'\] " \
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
            "op": "remove",
            "path": path + "/instanceOf:"
        }]
        return jsonpatch.JsonPatch(patches)
