import jsonpatch
import re
from cedar.patch import utils


class RecreateTemplateRequiredPatch(object):

    def __init__(self):
        self.description = "Fixes the property list of a template's required array"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = "/required"

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile(
            "array is too short: must have at least 9 elements but instance has \d elements at /required$|" +
            "instance value \('.+'\) not found in enum \(possible values: \['.+'\]\) at /required/\d+$")
        if pattern.match(error_description):
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_patch(self, doc, error):
        utils.check_argument_not_none("doc", doc)
        properties_list = self.get_all_properties(doc)
        patches = [{
            "op": "remove",
            "path": "/required"
        },
        {
            "op": "add",
            "value": properties_list,
            "path": "/required"
        }]
        return jsonpatch.JsonPatch(patches)

    @staticmethod
    def get_all_properties(doc):
        default_properties = [
            "@context",
            "@id",
            "schema:isBasedOn",
            "schema:name",
            "schema:description",
            "pav:createdOn",
            "pav:createdBy",
            "pav:lastUpdatedOn",
            "oslc:modifiedBy"]
        properties = list(doc["properties"].keys())
        for prop in properties:
            if prop not in default_properties:
                default_properties.append(prop)
        return default_properties