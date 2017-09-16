import jsonpatch
import re
from cedar.patch import utils


class RemovePageFromInnerUiPatch(object):

    def __init__(self):
        self.description = "Removes the 'page' field from a _ui of a template field or element"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: \['pages'\] " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/_ui$")
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
            "path": path + "/pages"
        }]
        return jsonpatch.JsonPatch(patches)
