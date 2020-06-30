import jsonpatch
import re
from cedar.patch import utils


class AddRdfsLabelToPropertiesPatch(object):

    def __init__(self):
        self.description = "Adds the missing rdfs:label in the properties object"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'rdfs:label'(,'.+')*\]\) " \
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
                "type": [
                    "string",
                    "null"
                ]
            },
            "path": path + "/rdfs:label"
        }]
        return jsonpatch.JsonPatch(patches)
