import jsonpatch
import re
import dpath
from cedar.patch import utils


class RestructureStaticTemplateFieldPatch(object):

    def __init__(self):
        self.description = "Restructure the model schema for the static template field"
        self.since = "1.1.0"
        self.path = None

    def is_applied(self, error_description):
        pattern = re.compile("instance value \('https://schema.metadatacenter.org/core/StaticTemplateField'\) not found in enum \(possible values: \['https://schema.metadatacenter.org/core/TemplateElement'\]\) at (/properties/[^/]+)*/properties/[^/]+/@type$")
        if pattern.match(error_description):
            self.path = self.get_user_property_path(error_description)
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
