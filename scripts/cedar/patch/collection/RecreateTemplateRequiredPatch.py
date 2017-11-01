import jsonpatch
import re
from cedar.patch import utils


class RecreateTemplateRequiredPatch(object):

    def __init__(self):
        self.description = "Fixes the property list of a template's required array"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "array is too short: must have at least 9 elements but instance has \d elements " \
            "at /required$" \
            "|" \
            "instance value \('.+'\) not found in enum \(possible values: \['.+'\]\) " \
            "at /required/\d+$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    def get_patch(self, error_message, doc=None):
        patches = [{
            "op": "remove",
            "path": "/required"
        },
        {
            "op": "add",
            "value": self.get_template_required_properties(doc),
            "path": "/required"
        }]
        return jsonpatch.JsonPatch(patches)


    def get_template_required_properties(self, template_object):
        user_properties = self.get_user_properties(template_object.get("properties"))
        required_properties = [
            "@context",
            "@id",
            "schema:isBasedOn",
            "schema:name",
            "schema:description",
            "pav:createdOn",
            "pav:createdBy",
            "pav:lastUpdatedOn",
            "oslc:modifiedBy"]  # mandatory property names
        required_properties.extend(user_properties)
        return required_properties

    @staticmethod
    def get_user_properties(properties_object):
        exclude_list = ["@context", "@id", "@type", "xsd", "schema", "pav", "oslc", "pav:createdOn",
                        "pav:createdBy", "pav:lastUpdatedOn", "oslc:modifiedBy"]
        property_names = list(properties_object.keys())
        return [item for item in property_names if item not in exclude_list]
