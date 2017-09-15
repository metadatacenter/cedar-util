import jsonpatch
import re
from cedar.patch import utils


class AddXsdToContextPropertiesPatch(object):

    def __init__(self):
        self.description = "Fixes the missing 'xsd' prefix label in the @context/properties object of a template"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile("object has missing required properties \(\[('.+',)*'xsd'(,'.+')*\]\) at /properties/@context/properties$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            return True
        else:
            return False

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
                    "http://www.w3.org/2001/XMLSchema#"
                ]
            },
            "path": path + "/xsd"
        },
        {
            "op": "add",
            "value": "xsd",
            "path": parent_path + "/required/0"
        }]
        return jsonpatch.JsonPatch(patches)
