import jsonpatch
import re
from cedar.patch import utils


class AddSchemaNameToContextPropertiesPatch(object):

    def __init__(self):
        self.description = "Fixes the missing 'schema:name' in the @context/properties object of a template"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'schema:name'(,'.+')*\]\) " \
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
                "type": "object",
                "properties": {
                    "@type": {
                        "type": "string",
                        "enum": [
                            "xsd:string"
                        ]
                    }
                }
            },
            "path": path + "/schema:name"
        },
        {
            "op": "add",
            "value": "schema:name",
            "path": parent_path + "/required/-"
        }]
        return jsonpatch.JsonPatch(patches)
