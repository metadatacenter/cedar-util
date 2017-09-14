import jsonpatch
import re
import dpath
from cedar.patch import utils


class AddProvenanceToFieldOrElementPatch(object):

    def __init__(self):
        self.description = "Add the missing provenance attributes into the template element or fields"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile("object has missing required properties " \
                             "\(\[('.+',)*'oslc:modifiedBy','pav:createdBy','pav:createdOn','pav:lastUpdatedOn'(,'.+')*\]\) " \
                             "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*$")
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

        patches = [{
            "op": "add",
            "value": None,
            "path": path + "/pav:createdOn"
        },
        {
            "op": "add",
            "value": None,
            "path": path + "/pav:createdBy"
        },
        {
            "op": "add",
            "value": None,
            "path": path + "/pav:lastUpdatedOn"
        },
        {
            "op": "add",
            "value": None,
            "path": path + "/oslc:modifiedBy"
        }]

        return jsonpatch.JsonPatch(patches)
