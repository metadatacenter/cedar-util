import jsonpatch
import re
from cedar.patch import utils


class AddIdToPropertiesPatch(object):

    def __init__(self):
        self.description = "Adds the missing @id in the properties object"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'@id'(,'.+')*\]\) " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties$")
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
            "value": {
                "type": "string",
                "format": "uri"
            },
            "path": path + "/@id"
        }]
        return jsonpatch.JsonPatch(patches)
