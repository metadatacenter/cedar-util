import jsonpatch
import re
import dpath
from cedar.patch import utils


class RestructureMultiValuedFieldPatch(object):

    def __init__(self):
        self.description = "Restructure the model schema of a multi-valued field (i.e., checkbox and multi-select list)"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=True)

        error_description = error
        is_applied = False
        pattern = re.compile("object has missing required properties \(\['items','minItems'\]\) at (/properties/[^/]+)+")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            if utils.is_multivalued_field(doc, at=self.path):
                is_applied = True
        return is_applied

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(doc, error):
        utils.check_argument_not_none("doc", doc)
        error_message = error
        path = utils.get_error_location(error_message)

        element_or_field = dpath.util.get(doc, path)

        patches = [{
            "op": "remove",
            "path": path
        },
        {
            "op": "add",
            "value": {},
            "path": path
        },
        {
            "op": "add",
            "value": "array",
            "path": path + "/type"
        },
        {
            "op": "add",
            "value": 1,
            "path": path + "/minItems"
        },
        {
            "op": "add",
            "value": element_or_field,
            "path": path + "/items"
        }]
        return jsonpatch.JsonPatch(patches)
