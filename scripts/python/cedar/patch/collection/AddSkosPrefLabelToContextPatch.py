import jsonpatch
import re
from python.cedar.patch import utils


class AddSkosPrefLabelToContextPatch(object):

    def __init__(self):
        self.description = "Fixes the missing skos:prefLabel in the @context object of a template-field"
        self.from_version = "1.0.0"
        self.to_version = "1.5.0"

    def is_applied(self, error_message, doc=None):
        resource_root = utils.get_parent_path(utils.get_error_location(error_message))
        if not utils.is_template_field(doc, resource_root):
            return False
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'skos:prefLabel'(,'.+')*\]\) " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/@context$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        patches = [{
            "op": "add",
            "value": {
                "@type": "xsd:string"
            },
            "path": path + "/skos:prefLabel"
        }]
        return jsonpatch.JsonPatch(patches)
