import jsonpatch
import re
import dpath
from collections import OrderedDict
from python.cedar.patch import utils


class RemoveArrayDuplicatesPatch(object):

    def __init__(self):
        self.description = "Removes duplicates in an array"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile("array must not contain duplicate elements at /.*$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)

        array_items = dpath.util.get(doc, path)
        non_duplicate_list = list(OrderedDict.fromkeys(array_items))

        patches = [{
            "op": "remove",
            "path": path
        },
        {
            "op": "add",
            "value": non_duplicate_list,
            "path": path
        }]
        return jsonpatch.JsonPatch(patches)
