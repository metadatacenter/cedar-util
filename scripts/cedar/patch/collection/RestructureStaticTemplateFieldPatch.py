import jsonpatch
import re
import dpath
from cedar.patch import utils


class RestructureStaticTemplateFieldPatch(object):

    def __init__(self):
        self.description = "Restructure the model schema for the static template field"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=True)

        error_description = error
        is_applied = False
        pattern = re.compile("instance value \('https://schema.metadatacenter.org/core/StaticTemplateField'\) not found in enum \(possible values: \['https://schema.metadatacenter.org/core/TemplateElement'\]\) at (/properties/[^/]+)*/properties/[^/]+/@type$")
        if pattern.match(error_description):
            self.path = self.get_user_property_path(error_description)
            if utils.is_static_template_field(doc, at=self.path):
                is_applied = True
        return is_applied

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_patch(self, doc, error):
        utils.check_argument_not_none("doc", doc)
        error_description = error
        path = self.get_user_property_path(error_description)

        patches = []
        if self.has_content(doc, path):
            patch = {
                "op": "move",
                "from": path + "/properties/_content",
                "path": path + "/_ui/_content"
            }
            patches.append(patch)

        patch = {
            "op": "remove",
            "path": path + "/properties",
        }
        patches.append(patch)
        patch = {
            "op": "remove",
            "path": path + "/required",
        }
        patches.append(patch)
        return jsonpatch.JsonPatch(patches)

    @staticmethod
    def get_user_property_path(error_description):
        original_path = utils.get_error_location(error_description)
        user_property_path = original_path[:original_path.rfind('/@type')]
        return user_property_path

    @staticmethod
    def has_content(doc, path):
        properties_path = path + "/properties"
        properties = dpath.util.get(doc, properties_path)
        return "_content" in properties
