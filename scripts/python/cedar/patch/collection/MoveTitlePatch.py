import jsonpatch
import re
from cedar.utils import general_utils as utils


class MoveTitlePatch(object):

    def __init__(self):
        self.description = "Move the title a template, element or field from _ui to the document root"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: \[('.+',)*'title'(,'.+')*\] " \
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
            "from": ui_path + "/title",
            "path": root_path + "/schema:name"
        }]
        return jsonpatch.JsonPatch(patches)
