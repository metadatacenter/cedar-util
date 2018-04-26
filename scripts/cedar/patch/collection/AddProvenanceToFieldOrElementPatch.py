import jsonpatch
import re
import dpath
from cedar.patch import utils


class AddProvenanceToFieldOrElementPatch(object):

    def __init__(self):
        self.description = "Add the missing provenance attributes into the template element or fields"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'oslc:modifiedBy','pav:createdBy','pav:createdOn','pav:lastUpdatedOn'(,'.+')*\]\) " \
            "at ((/properties/[^/]+/items)*(/properties/[^/@]+)*)*$")
        path = utils.get_error_location(error_message)
        return pattern.match(error_message) and (utils.is_template_element(doc, at=path) or utils.is_template_field(doc, at=path))

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)

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
