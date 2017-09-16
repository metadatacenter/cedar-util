import jsonpatch
import re
from cedar.patch import utils


class AddSchemaVersionPatch(object):

    def __init__(self):
        self.description = "Add the missing schema:schemaVersion field in a template, element or field"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'schema:schemaVersion'(,'.+')*\]\) " \
            "at /.*$")
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
            "value": "1.1.0",
            "path": path + "/schema:schemaVersion"
        }]
        return jsonpatch.JsonPatch(patches)
