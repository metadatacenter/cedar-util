import jsonpatch
import re
from cedar.patch import utils


class AddValueConstraintsToFieldOrElementPatch(object):

    def __init__(self):
        self.description = "Adds the missing _valueConstraints in a template element or field"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=True)

        error_description = error
        is_applied = False
        pattern = re.compile("object has missing required properties \(\[('.+',)*'_valueConstraints'(,'.+')*\]\) at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            if utils.is_template_field(doc, at=self.path):
                is_applied = True
        return is_applied

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(doc, error):
        error_description = error
        path = utils.get_error_location(error_description)
        patches = [{
            "op": "add",
            "value": {
                "requiredValue": False
            },
            "path": path + "/_valueConstraints"
        }]
        return jsonpatch.JsonPatch(patches)
