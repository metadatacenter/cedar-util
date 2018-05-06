import jsonpatch
import re
from cedar.patch import utils


class AddMultipleChoiceToValueConstraintsPatch(object):

    def __init__(self):
        self.description = "Fixes the missing multipleChoice in the _valueConstraints of a multivalued field"
        self.from_version = "1.2.0"
        self.to_version = "1.3.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'multipleChoice'(,'.+')*\]\) " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/_valueConstraints$")
        path = utils.get_error_location(error_message)
        path = utils.get_parent_path(path)
        return pattern.match(error_message) and utils.is_multivalued_field(doc, at=path)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        patches = [{
            "op": "add",
            "value": True,
            "path": path + "/multipleChoice"
        }]
        return jsonpatch.JsonPatch(patches)
