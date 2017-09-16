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

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_patch(self, doc, error):
        utils.check_argument_not_none("doc", doc)
        error_description = error
        path = utils.get_error_location(error_description)

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
