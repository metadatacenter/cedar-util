import jsonpatch
import re
from cedar.patch import utils


class AddPavDerivedFromToContextPropertiesPatch(object):

    def __init__(self):
        self.description = "Allow instances to have the pav:derivedFrom field"
        self.from_version = "1.4.0"
        self.to_version = "1.6.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\['pav:derivedFrom'\]\) " \
            "at /properties$")
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
            "path": path + "/pav:derivedFrom"
        }]
        return jsonpatch.JsonPatch(patches)
