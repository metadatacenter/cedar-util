import jsonpatch
import re
import dpath
from python.cedar.patch import utils


class RestructureStaticTemplateFieldPatch(object):

    def __init__(self):
        self.description = "Restructure the model schema for the static template field"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance value \('https://schema.metadatacenter.org/core/StaticTemplateField'\) not found in enum " \
            "\(possible values: \['https://schema.metadatacenter.org/core/TemplateElement'\]\) " \
            "at (/properties/[^/]+)*/properties/[^/]+/@type$")
        is_applied = False
        if pattern.match(error_message):
            path = utils.get_error_location(error_message)
            parent_path = utils.get_parent_path(path)
            if utils.is_static_template_field(doc, at=parent_path):
                is_applied = True
        return is_applied

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    def get_patch(self, error_message, doc=None):
        path = utils.get_error_location(error_message)
        parent_path = utils.get_parent_path(path)

        patches = []
        if self.has_content(doc, parent_path):
            patch = {
                "op": "move",
                "from": parent_path + "/properties/_content",
                "path": parent_path + "/_ui/_content"
            }
            patches.append(patch)

        patch = {
            "op": "remove",
            "path": parent_path + "/properties",
        }
        patches.append(patch)
        patch = {
            "op": "remove",
            "path": parent_path + "/required",
        }
        patches.append(patch)
        return jsonpatch.JsonPatch(patches)

    @staticmethod
    def has_content(doc, path):
        properties_path = path + "/properties"
        properties = dpath.util.get(doc, properties_path)
        return "_content" in properties
