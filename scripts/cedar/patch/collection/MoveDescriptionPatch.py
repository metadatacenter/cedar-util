import jsonpatch
import re
from cedar.patch import utils


class MoveDescriptionPatch(object):

    def __init__(self):
        self.description = "Move the description a template, element or field from _ui to the document root"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: \[('.+',)*'description'(,'.+')*\] " \
            "at (/.+)?/_ui$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        ui_path = utils.get_error_location(error_message)
        root_path = utils.get_parent_path(ui_path)
        patches = [{
            "op": "move",
            "from": ui_path + "/description",
            "path": root_path + "/schema:description"
        }]
        return jsonpatch.JsonPatch(patches)
