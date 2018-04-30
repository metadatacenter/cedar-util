import jsonpatch
import re
from cedar.patch import utils


class AddVersioningInNestedMultiElementPatch(object):

    def __init__(self):
        self.description = "Add versioning in deep nested multi-elements"
        self.from_version = "1.3.0"
        self.to_version = "1.4.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance failed to match exactly one schema \(matched 0 out of 2\) " \
            "at ((/properties/[^/]+/items)?(/properties/[^/]+)?)*/properties/[^/]+/items$")
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
            "value": "http://purl.org/ontology/bibo/",
            "path": path + "/@context/bibo"
        },
        {
            "op": "add",
            "value": "0.0.1",
            "path": path + "/pav:version"
        },
        {
            "op": "add",
            "value": "bibo:draft",
            "path": path + "/bibo:status"
        }]
        return jsonpatch.JsonPatch(patches)
