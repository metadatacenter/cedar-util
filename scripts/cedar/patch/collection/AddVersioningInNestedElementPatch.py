import jsonpatch
import re
from cedar.patch import utils
import dpath

class AddVersioningInNestedElementPatch(object):

    def __init__(self):
        self.description = "Add versioning in deep nested elements"
        self.from_version = "1.3.0"
        self.to_version = "1.4.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance failed to match exactly one schema \(matched 0 out of 5\) " \
            "at ((/properties/[^/]+/items)?(/properties/[^/]+)?)*/properties/[^/]+$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    def get_patch(self, error_message, doc=None):
        path = self.get_path(error_message, doc)
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

    @staticmethod
    def get_path(error_message, doc):
        path = utils.get_error_location(error_message)
        element_node = utils.get_json_node(doc, path)
        if element_node.get("type") == "array":
            path = path + "/items"
        return path