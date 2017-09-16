import jsonpatch
import re
import dpath
from cedar.patch import utils


class AddPropertyLabelsToUiPatch(object):

    def __init__(self):
        self.description = "Adds the missing propertyLabels field in the _ui object"
        self.from_version = None
        self.to_version = "1.1.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'propertyLabels'(,'.+')*\]\) " \
            "at (/.+)?/_ui$")
        is_applied = False
        if pattern.match(error_message):
            path = utils.get_error_location(error_message)
            parent_path = utils.get_parent_path(path)
            if utils.is_template(doc, at=parent_path) or utils.is_template_element(doc, at=parent_path):
                is_applied = True
        return is_applied

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_patch(self, doc, error):
        utils.check_argument_not_none("doc", doc)
        error_description = error
        path = utils.get_error_location(error_description)
        property_labels = self.get_property_labels(doc, path)
        patches = [{
            "op": "add",
            "value": property_labels,
            "path": path + "/propertyLabels"
        }]
        return jsonpatch.JsonPatch(patches)

    def get_property_labels(self, doc, path):
        user_properties = self.get_user_properties(doc, path)
        property_labels = {}
        for prop in user_properties:
            property_labels[prop] = self.to_title_case(prop)
        return property_labels

    @staticmethod
    def get_user_properties(doc, path):
        parent_path = utils.get_parent_path(path)
        properties = list(dpath.util.get(doc, parent_path + "/properties").keys())
        system_properties = [
            "@context",
            "@id",
            "@type",
            "schema:isBasedOn",
            "schema:name",
            "schema:description",
            "pav:createdOn",
            "pav:createdBy",
            "pav:lastUpdatedOn",
            "oslc:modifiedBy"]
        return [prop for prop in properties if prop not in system_properties]

    @staticmethod
    def to_title_case(text):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).title()
