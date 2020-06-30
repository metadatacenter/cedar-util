import jsonpatch
import re
from cedar.patch import utils


class AddContentToUiPatch(object):

    def __init__(self):
        self.description = "Adds the missing '_content' field in the _ui object for the static template field"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'_content'(,'.+')*\]\) " \
            "at (/.+)?/_ui$")
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
            "value": None,
            "path": path + "/_content"
        }]
        return jsonpatch.JsonPatch(patches)


