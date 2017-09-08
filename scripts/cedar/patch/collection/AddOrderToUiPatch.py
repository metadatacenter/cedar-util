import jsonpatch
import re
import dpath
from cedar.patch import utils


class AddOrderToUiPatch(object):

    def __init__(self):
        self.description = "Adds the missing order field in the _ui object"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=True)

        error_description = error
        is_applied = False
        pattern = re.compile("object has missing required properties \(\[('.+',)*'order'(,'.+')*\]\) at (/.+)?/_ui$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            parent_path = utils.get_parent_path(self.path)
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
