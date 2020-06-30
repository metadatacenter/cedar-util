import jsonpatch
import re
import dpath
from cedar.patch import utils


class AddRequiredToFieldOrElementPatch(object):

    def __init__(self):
        self.description = "Add the missing required field in a template element or field"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\['required'\]\) " \
            "at ((/properties/[^/]+/items)*(/properties/[^/@]+)*)*$")
        is_applied = False
        if pattern.match(error_message):
            path = utils.get_error_location(error_message)
            if utils.is_template_element(doc, at=path) or utils.is_template_field(doc, at=path):
                is_applied = True
        return is_applied

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    def get_patch(self, error_message, doc=None):
        path = utils.get_error_location(error_message)
        property_object = utils.get_json_node(doc, path)
        patches = [{
            "op": "add",
            "value": self.get_required_properties(property_object),
            "path": path + "/required"
        }]
        return jsonpatch.JsonPatch(patches)

    @staticmethod
    def get_required_properties(property_object):
        exclude_list = ["@type", "xsd", "schema", "pav", "oslc", "rdfs:label", "pav:createdOn",
                        "pav:createdBy", "pav:lastUpdatedOn", "oslc:modifiedBy"]
        properties_object = property_object.get("properties")
        property_names = list(properties_object.keys())
        return [item for item in property_names if item not in exclude_list]
