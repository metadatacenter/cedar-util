import jsonpatch
import re
from cedar.patch import utils


class RemovePatternPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the requirement to have 'patternProperties' field in @context"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"
        self.path = None

    def is_applied(self, error_description, template=None):
        if template is None:
            pass # Just ignore

        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: \['patternProperties'\] at /.*$")
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
        if doc is None:
            pass  # Just ignore

        if self.path is None and path is None:
            raise Exception("The method requires the 'path' argument")

        if path is not None:
            self.path = path

        patches = []
        patch = {
            "op": "remove",
            "path": self.path + "/patternProperties"
        }
        patches.append(patch)

        return patches