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

    @staticmethod
    def is_applied(error_message, doc=None):
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
