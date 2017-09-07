import jsonpatch
import re
import dpath
from collections import OrderedDict
from cedar.patch import utils


class RemoveArrayDuplicatesPatch(object):

    def __init__(self):
        self.description = "Removes duplicates in an array"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile("array must not contain duplicate elements at /.*$")
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
        utils.check_argument('doc', doc, isreq=True)
        utils.check_argument('path', path, isreq=False)

        array_items = dpath.util.get(doc, self.path)
        non_duplicate_list = list(OrderedDict.fromkeys(array_items))

        patches = []
        patch = {
            "op": "remove",
            "path": self.path
        }
        patches.append(patch)
        patch = {
            "op": "add",
            "value": non_duplicate_list,
            "path": self.path
        }
        patches.append(patch)

        return patches
