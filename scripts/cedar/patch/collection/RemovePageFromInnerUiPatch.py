import jsonpatch
import re
from cedar.patch import utils


class RemovePageFromInnerUiPatch(object):

    def __init__(self):
        self.description = "Removes the page field from a _ui that belongs to a template field or element"
        self.since = "1.1.0"
        self.path = None

    def is_applied(self, error_description):
        pattern = re.compile("object instance has properties which are not allowed by the schema: \['pages'\] at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/_ui$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description) + "/pages"
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc, path=None):
        if self.path is None and path is None:
            raise Exception("The method required a 'path' location")

        if path is not None:
            self.path = path

        patches = []
        patch = {
            "op": "remove",
            "path": self.path
        }
        patches.append(patch)

        return patches
