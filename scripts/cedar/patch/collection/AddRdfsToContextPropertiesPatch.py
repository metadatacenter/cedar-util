import jsonpatch
import re
from cedar.patch import utils


class AddRdfsToContextPropertiesPatch(object):

    def __init__(self):
        self.description = "Fixes the missing 'rdfs' in the @context/properties object of a template"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'rdfs'(,'.+')*\]\) " \
            "at /properties/@context/properties$")
        return pattern.match(error_message)

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(doc, error):
        utils.check_argument_not_none("doc", doc)

        error_description = error
        path = utils.get_error_location(error_description)
        parent_path = utils.get_parent_path(path)

        patches = [{
            "op": "add",
            "value": {
                "type": "string",
                "format": "uri",
                "enum": [
                    "http://www.w3.org/2000/01/rdf-schema#"
                ]
            },
            "path": path + "/rdfs"
        },
        {
            "op": "add",
            "value": "rdfs",
            "path": parent_path + "/required/1"
        }]
        return jsonpatch.JsonPatch(patches)
