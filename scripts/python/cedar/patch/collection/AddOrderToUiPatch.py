import jsonpatch
import re
import dpath
from cedar.utils import general_utils as utils


class AddOrderToUiPatch(object):

    def __init__(self):
        self.description = "Adds the missing order field in the _ui object"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'order'(,'.+')*\]\) " \
            "at (/.+)?/_ui$")
        is_applied = False
        if pattern.match(error_message):
            path = utils.get_error_location(error_message)
            parent_path = utils.get_parent_path(path)
            if utils.is_template(doc, at=parent_path) or utils.is_template_element(doc, at=parent_path):
                is_applied = True
        return is_applied

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    def get_patch(self, error_message, doc=None):
        path = utils.get_error_location(error_message)
        user_properties = self.get_user_properties(doc, path)
        patches = [{
            "op": "add",
            "value": user_properties,
            "path": path + "/order"
        }]
        return jsonpatch.JsonPatch(patches)

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
