import jsonpatch
import re
import dpath
from cedar.patch import utils


class AddPropertyLabelsToUiPatch(object):

    def __init__(self):
        self.description = "Adds the missing propertyLabels field in the _ui object"
        self.since = "1.1.0"
        self.path = None

    def is_applied(self, error_description):
        pattern = re.compile(
            "object has missing required properties \(\[('.+',)*'propertyLabels'(,'.+')*\]\) at (/.+)?/_ui$")
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

        property_labels = self.get_property_labels(doc)

        patches = []
        patch = {
            "op": "add",
            "value": property_labels,
            "path": self.path + "/propertyLabels"
        }
        patches.append(patch)

        return patches

    def get_property_labels(self, doc):
        user_properties = self.get_user_properties(doc)
        property_labels = {}
        for prop in user_properties:
            property_labels[prop] = self.to_title_case(prop)
        return property_labels

    def get_user_properties(self, doc):
        parent_path = self.path[:self.path.rfind('/')]
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

    def to_title_case(self, text):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).title()
