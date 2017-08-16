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

    def is_applied(self, error_description, template=None):
        pattern = re.compile("object has missing required properties \(\[('.+',)*'schema:schemaVersion'(,'.+')*\]\) at /.*$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            return True
        else:
            return False

    def apply(self, doc, path=None):
        print(doc)
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        print("HERE!!!")
        print(patched_doc)
        return patched_doc

    def get_json_patch(self, doc, path=None):
        if self.path is None and path is None:
            raise Exception("The method required a 'path' location")

        if path is not None:
            self.path = path

        patches = []
        patch = {
            "op": "add",
            "value": "1.1.0",
            "path": self.path
        }
        patches.append(patch)

        return patches
