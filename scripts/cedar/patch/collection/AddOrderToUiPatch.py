import jsonpatch
import re
import dpath
from cedar.patch import utils
from cedar.patch.collection import utils as cedar_helper


class AddOrderToUiPatch(object):

    def __init__(self):
        self.description = "Adds the missing order field in the _ui object"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error_description, template=None):
        utils.check_argument_not_none(template, "The method required a template argument")

        is_applied = False
        pattern = re.compile("object has missing required properties \(\[('.+',)*'order'(,'.+')*\]\) at (/.+)?/_ui$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            resource_obj = self.get_resource_object(template, self.path)
            if cedar_helper.is_template(resource_obj) or cedar_helper.is_template_element(resource_obj):
                is_applied = True
        return is_applied

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc=None, path=None):
        utils.check_argument_not_none(doc, "The method requires the 'doc' argument")

        if self.path is None and path is None:
            raise Exception("The method requires the 'path' argument")

        if path is not None:
            self.path = path

        user_properties = self.get_user_properties(doc)

        patches = []
        patch = {
            "op": "add",
            "value": user_properties,
            "path": self.path + "/order"
        }
        patches.append(patch)

        return patches

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
    def get_resource_object(template, path):
        resource_object = template
        parent_path = path[:path.rfind('/')]
        if parent_path:
            resource_object = dpath.util.get(template, parent_path)
        return resource_object
