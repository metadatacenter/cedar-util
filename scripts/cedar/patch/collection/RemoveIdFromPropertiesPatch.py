import jsonpatch
import re
from cedar.patch import utils


class RemoveIdFromPropertiesPatch(object):

    def __init__(self):
        self.description = "Remove the invalid @id property"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile("object has invalid properties \(\['@id'\]\) at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties$|" +
                             "object instance has properties which are not allowed by the schema: \['@id'\] at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description) + "/@id"
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
            "op": "remove",
            "path": self.path
        }
        patches.append(patch)

        return patches
