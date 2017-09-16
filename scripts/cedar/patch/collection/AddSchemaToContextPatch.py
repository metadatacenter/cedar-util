import jsonpatch
import re
from cedar.patch import utils


class AddSchemaToContextPatch(object):

    def __init__(self):
        self.description = "Fixes the missing 'schema' prefix label in the @context object of a template"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'schema'(,'.+')*\]\) " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/@context$")
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
            "value": "http://schema.org/",
            "path": path + "/schema"
        }]
        return jsonpatch.JsonPatch(patches)
