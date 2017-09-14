import jsonpatch
import re
from cedar.patch import utils


class RecreateElementRequiredPatch(object):

    def __init__(self):
        self.description = "Fixes the property list of the element's required array"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile(
            "array is too short: must have at least 2 elements but instance has \d elements at ((/properties/[^/]+/items)*(/properties/[^/]+)*)+/required$|" +
            "instance value \('.+'\) not found in enum \(possible values: \['.+'\]\) at ((/properties/[^/]+/items)*(/properties/[^/]+)*)+/required/\d+$")
        if pattern.match(error_description):
            path = utils.get_error_location(error_description)
            property_path = path[:path.rfind("/required")]
            property_object = utils.get_json_object(doc, property_path)
            if utils.is_template_element(property_object):
                return True
            else:
                return False
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_patch(self, doc, error):
        utils.check_argument_not_none("doc", doc)
        error_description = error
        path = utils.get_error_location(error_description)
        property_path = path[:path.rfind("/required")]

        properties_list = self.get_all_properties(doc)
        patches = [{
            "op": "remove",
            "path": property_path + "/required"
        },
        {
            "op": "add",
            "value": properties_list,
            "path": property_path + "/required"
        }]
        return jsonpatch.JsonPatch(patches)

    @staticmethod
    def get_all_properties(doc):
        default_properties = [
            "@context",
            "@id"
        ]
        properties = list(doc["properties"].keys())
        for prop in properties:
            if prop not in default_properties:
                default_properties.append(prop)
        return default_properties
