import jsonpatch
import re
import dpath
from cedar.patch import utils
from cedar.patch.collection import utils as cedar_helper


class AddValueConstraintsToFieldOrElementPatch(object):

    def __init__(self):
        self.description = "Adds the missing _valueConstraints in a template element or field"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error_description, template=None):
        utils.check_argument_not_none(template, "The method required a template object")

        is_applied = False
        pattern = re.compile("object has missing required properties \(\[('.+',)*'_valueConstraints'(,'.+')*\]\) at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            resource_obj = self.get_resource_object(template, self.path)
            if cedar_helper.is_template_field(resource_obj):
                is_applied = True
        return is_applied

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
            "value": {
                "requiredValue": False
            },
            "path": self.path + "/_valueConstraints"
        }
        patches.append(patch)

        return patches

    @staticmethod
    def get_resource_object(template, path):
        return dpath.util.get(template, path)