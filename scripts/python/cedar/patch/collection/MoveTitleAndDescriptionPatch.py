import jsonpatch
import re
from python.cedar.patch import utils


class MoveTitleAndDescriptionPatch(object):

    def __init__(self):
        self.description = "Move the title and description of a template, element or field from _ui to the document root"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\['schema:description','schema:name'\]\) " \
            "at (/?(/properties/[^/]+/items)*(/properties/[^/]+)*)*$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        patches = [{
            "op": "move",
            "from": path + "/_ui/title",
            "path": path + "/schema:name"
        },
        {
            "op": "move",
            "from": path + "/_ui/description",
            "path": path + "/schema:description"
        }]
        return jsonpatch.JsonPatch(patches)
