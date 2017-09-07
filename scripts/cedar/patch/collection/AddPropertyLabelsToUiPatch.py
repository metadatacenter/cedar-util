import jsonpatch
import re
import dpath
from cedar.patch import utils
from cedar.patch.collection import utils as cedar_helper


class AddPropertyLabelsToUiPatch(object):

    def __init__(self):
        self.description = "Adds the missing propertyLabels field in the _ui object"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=True)

        error_description = error
        is_applied = False
        pattern = re.compile("object has missing required properties \(\[('.+',)*'propertyLabels'(,'.+')*\]\) at (/.+)?/_ui$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            resource_obj = self.get_resource_object(doc, self.path)
            if cedar_helper.is_template(resource_obj) or cedar_helper.is_template_element(resource_obj):
                is_applied = True
        return is_applied

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc=None, path=None):
        utils.check_argument('doc', doc, isreq=True)
        utils.check_argument('path', path, isreq=False)

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

    @staticmethod
    def to_title_case(text):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).title()

    @staticmethod
    def get_resource_object(template, path):
        resource_object = template
        parent_path = path[:path.rfind('/')]
        if parent_path:
            resource_object = dpath.util.get(template, parent_path)
        return resource_object