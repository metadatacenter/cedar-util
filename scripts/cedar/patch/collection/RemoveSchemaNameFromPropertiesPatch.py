import jsonpatch
import re
from cedar.patch import utils


class RemoveSchemaNameFromPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the schema:name in the properties of a template field or element"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)

        error_description = error
        pattern = re.compile("object instance has properties which are not allowed by the schema: " \
                             "\[('.+',)*'schema:name'(,'.+')*\] " \
                             "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties$")
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
        utils.check_argument_not_none("error", error)

        error_description = error
        path = utils.get_error_location(error_description)

        property_path = path[:path.rfind("/properties")]
        property_object = utils.get_json_object(doc, property_path)
        required_list = property_object.get("required")

        patches = [{
            "op": "remove",
            "path": path + "/schema:name"
        },
        {
            "op": "replace",
            "value": [item for item in required_list if item != "schema:name"],
            "path": property_path + "/required"
        }]
        return jsonpatch.JsonPatch(patches)
