import jsonpatch
import re
from cedar.patch import utils


class MoveTitleAndDescriptionPatch(object):

    def __init__(self):
        self.description = "Move the title and description of a template, element or field from _ui to the document root"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object has missing required properties " \
            "\(\['schema:description','schema:name'\]\) " \
            "at (/?(/properties/[^/]+/items)*(/properties/[^/]+)*)*$")
        return pattern.match(error_message)

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_patch(self, doc, error):
        error_description = error
        path = utils.get_error_location(error_description)

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
