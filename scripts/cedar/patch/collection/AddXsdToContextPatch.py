import jsonpatch
import re
from cedar.patch import utils


class AddXsdToContextPatch(object):

    def __init__(self):
        self.description = "Fixes the missing xsd prefix label in the @context object of a template"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error_description, template=None):
        pattern = re.compile("object has missing required properties \(\[('.+',)*'xsd'(,'.+')*\]\) at /@context$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
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
            "op": "add",
            "value": "http://www.w3.org/2001/XMLSchema#",
            "path": self.path + "/xsd"
        }
        patches.append(patch)
        return patches
