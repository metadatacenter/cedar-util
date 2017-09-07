import jsonpatch
import re
from cedar.patch import utils


class FillEmptyValuePatch(object):

    def __init__(self):
        self.description = "Fills empty fields with a default 'blank' string value"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile("string '' is too short \(length: 0, required minimum: 1\) at /.*$")
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

        default_value = "blank"

        patches = []
        patch = {
            "op": "add",
            "value": default_value,
            "path": self.path
        }
        patches.append(patch)

        return patches
