import jsonpatch
import re
from cedar.patch import utils


class AddSchemaPropsToPropertiesPatch(object):

    def __init__(self):
        self.description = "Fixes the missing schema fields (i.e., 'schema:name','schema:description'," \
                           "'schema:isBasedOn' in the properties object of a template"
        self.from_version = "1.2.0"
        self.to_version = "1.3.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'schema:description','schema:isBasedOn','schema:name'(,'.+')*\]\) " \
            "at /properties")
        return pattern.match(error_message) and utils.is_template(doc)

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
            "path": "/properties/schema:isBasedOn"
        },
        {
            "op": "add",
            "value": {
                "type": "string",
                "minLength": 1
            },
            "path": "/properties/schema:name"
        },
        {
            "op": "add",
            "value": {
                "type": "string"
            },
            "path": "/properties/schema:description"
        }]
        return jsonpatch.JsonPatch(patches)
