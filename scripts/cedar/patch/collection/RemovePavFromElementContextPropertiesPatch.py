import jsonpatch
import re
from cedar.patch import utils


class RemovePavFromElementContextPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the 'pav' prefix in the @context/properties object of an element"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)

        error_description = error
        pattern = re.compile("object instance has properties which are not allowed by the schema: " \
                             "\[('.+',)*'pav'(,'.+')*\] at " \
                             "((/properties/[^/@]+/items)*(/properties/[^/@]+)*)*/properties/@context/properties$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(doc, error):
        utils.check_argument_not_none("doc", doc)

        error_description = error
        path = utils.get_error_location(error_description)

        parent_object, parent_path = utils.get_parent_object(doc, path)
        required_list = parent_object.get("required")

        patches = [{
            "op": "remove",
            "path": path + "/pav"
        },
        {
            "op": "replace",
            "value": [item for item in required_list if item != "pav"],
            "path": parent_path + "/required"
        }]
        return jsonpatch.JsonPatch(patches)
