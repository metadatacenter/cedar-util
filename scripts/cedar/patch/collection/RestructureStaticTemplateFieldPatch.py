import jsonpatch
import re
import dpath
from cedar.patch import utils
from cedar.patch.collection import utils as cedar_helper


class RestructureStaticTemplateFieldPatch(object):

    def __init__(self):
        self.description = "Restructure the model schema for the static template field"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error_description, template=None):
        utils.check_argument_not_none(template, "The method required a template object")

        is_applied = False
        pattern = re.compile("instance value \('https://schema.metadatacenter.org/core/StaticTemplateField'\) not found in enum \(possible values: \['https://schema.metadatacenter.org/core/TemplateElement'\]\) at (/properties/[^/]+)*/properties/[^/]+/@type$")
        if pattern.match(error_description):
            self.path = self.get_user_property_path(error_description)
            resource_obj = self.get_resource_object(template, self.path)
            if cedar_helper.is_static_template_field(resource_obj):
                is_applied = True
        return is_applied

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc, path=None):
        if self.path is None and path is None:
            raise Exception("The method required a 'path' location")

        if path is not None:
            self.path = path

        patches = []
        if self.has_content(doc):
            patch = {
                "op": "move",
                "from": self.path + "/properties/_content",
                "path": self.path + "/_ui/_content"
            }
            patches.append(patch)
        patch = {
            "op": "remove",
            "path": self.path + "/properties",
        }
        patches.append(patch)
        patch = {
            "op": "remove",
            "path": self.path + "/required",
        }
        patches.append(patch)
        return patches

    def get_user_property_path(self, error_description):
        original_path = utils.get_error_location(error_description)
        user_property_path = original_path[:original_path.rfind('/@type')]
        return user_property_path

    def has_content(self, doc):
        properties_path = self.path + "/properties"
        properties = dpath.util.get(doc, properties_path)
        return "_content" in properties

    @staticmethod
    def get_resource_object(template, path):
        resource_object = template
        parent_path = path[:path.rfind('/')]
        if parent_path:
            resource_object = dpath.util.get(template, parent_path)
        return resource_object