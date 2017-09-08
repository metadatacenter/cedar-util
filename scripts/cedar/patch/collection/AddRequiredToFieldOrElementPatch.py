import jsonpatch
import re
import dpath
from cedar.patch import utils


class AddRequiredToFieldOrElementPatch(object):

    def __init__(self):
        self.description = "Add the missing required field in a template element or field"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile("object has missing required properties \(\['required'\]\) at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            if not utils.is_static_template_field(doc):
                return True
            else:
                return False
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_patch(self, doc, error):
        error_description = error
        path = utils.get_error_location(error_description)
        user_property = self.get_all_properties(doc, path)
        patches = [{
            "op": "add",
            "value": user_property,
            "path": path + "/required"
        }]
        return jsonpatch.JsonPatch(patches)

    @staticmethod
    def get_all_properties(doc, path):
        properties = list(dpath.util.get(doc, path + "/properties").keys())
        system_properties = [
            "@id",
            "@type",
            "_valueLabel",
            "pav:createdOn",
            "pav:createdBy",
            "pav:lastUpdatedOn",
            "oslc:modifiedBy"]
        return [prop for prop in properties if prop not in system_properties]
