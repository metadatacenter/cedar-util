import jsonpatch
import re
from cedar.patch import utils


class RemoveSelectionTypeFromUiPatch(object):

    def __init__(self):
        self.description = "Removes the 'selectionType' field in the _ui object"
        self.from_version = "1.2.0"
        self.to_version = "1.3.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: \['selectionType'\] " \
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
            "op": "remove",
            "path": path + "/selectionType"
        }]
        return jsonpatch.JsonPatch(patches)
