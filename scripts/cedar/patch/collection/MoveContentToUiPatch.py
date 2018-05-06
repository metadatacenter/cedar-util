import jsonpatch
import re
from cedar.patch import utils


class MoveContentToUiPatch(object):

    def __init__(self):
        self.description = "Move _content object to the _ui field"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: " \
            "\['_content'\] " \
            "at (/properties/[^/]+)*/properties$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        parent_path = utils.get_parent_path(path)
        patches = [{
            "op": "move",
            "from": path + "/_content",
            "path": parent_path + "/_ui/_content"
        }]
        return jsonpatch.JsonPatch(patches)
