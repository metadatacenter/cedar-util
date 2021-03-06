import jsonpatch
import re
from cedar.utils import general_utils as utils


class AddSkosToContextPropertiesPatch(object):

    def __init__(self):
        self.description = "Fixes the missing 'skos' prefix label in the @context/properties object of a template"
        self.from_version = "1.0.0"
        self.to_version = "1.5.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'skos'(,'.+')*\]\) " \
            "at /properties/@context/properties$")
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
            "op": "add",
            "value": {
                "type": "string",
                "format": "uri",
                "enum": [
                    "http://www.w3.org/2004/02/skos/core#"
                ]
            },
            "path": path + "/skos"
        },
        {
            "op": "add",
            "value": "skos",
            "path": parent_path + "/required/-"
        }]
        return jsonpatch.JsonPatch(patches)
