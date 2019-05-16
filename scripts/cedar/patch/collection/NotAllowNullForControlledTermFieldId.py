import jsonpatch
import re
from cedar.patch import utils


class NotAllowNullForControlledTermFieldId(object):

    def __init__(self):
        self.description = "Removes the option to have a 'null' value in the @id field of a controlled-term field"
        self.from_version = "1.5.0"
        self.to_version = "1.6.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance value \(\['string','null'\]\) not found in enum \(possible values: \['string'\]\) " \
            "at /properties/.*/properties/@id/type$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        patches = [{
            "op": "replace",
            "value": "string",
            "path": path
        }]
        return jsonpatch.JsonPatch(patches)