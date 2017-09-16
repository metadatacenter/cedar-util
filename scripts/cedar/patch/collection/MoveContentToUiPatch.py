import jsonpatch
import re
from cedar.patch import utils


class MoveContentToUiPatch(object):

    def __init__(self):
        self.description = "Move _content object to the _ui field"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: " \
            "\['_content'\] " \
            "at (/properties/[^/]+)*/properties$")
        return pattern.match(error_message)

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(doc, error):
        error_description = error
        path = utils.get_error_location(error_description)
        parent_path = utils.get_parent_path(path)
        patches = [{
            "op": "move",
            "from": path + "/_content",
            "path": parent_path + "/_ui/_content"
        }]
        return jsonpatch.JsonPatch(patches)
