import jsonpatch
import re
import dpath
from cedar.patch import utils


class AddSchemaVersionPatch(object):

    def __init__(self):
        self.description = "Add the missing required field in a template element or field"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile("object has missing required properties \(\[('.+',)*'schema:schemaVersion'(,'.+')*\]\) at /.*$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc=None, path=None):
        utils.check_argument('doc', doc, isreq=False)
        utils.check_argument('path', path, isreq=False)

        patches = []
        patch = {
            "op": "add",
            "value": "1.1.0",
            "path": self.path + "/schema:schemaVersion"
        }
        patches.append(patch)

        return patches
