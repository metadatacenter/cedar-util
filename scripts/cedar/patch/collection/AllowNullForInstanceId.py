import jsonpatch
import re
from cedar.patch import utils


class AllowNullForInstanceId(object):

    def __init__(self):
        self.description = "Allow template instances to have a null ID value"
        self.from_version = "1.5.0"
        self.to_version = "1.6.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance type \(string\) does not match any allowed primitive type \(allowed: \['array'\]\) " \
            "at /properties/@id/type$")
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
            "path": path
        },
        {
            "op": "add",
            "value": ["string", "null"],
            "path": path
        }]
        return jsonpatch.JsonPatch(patches)
