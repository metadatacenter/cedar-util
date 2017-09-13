import jsonpatch
import re
from cedar.patch import utils


class RemoveProvenanceFromFieldOrElementPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the provenance fields (i.e., 'oslc:modifiedBy','pav:createdBy'," \
                           "'pav:createdOn','pav:lastUpdatedOn' in the properties of a template field or element"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)

        error_description = error
        pattern = re.compile("object instance has properties which are not allowed by the schema: \[('.+',)*" \
                             "'oslc:modifiedBy','pav:createdBy','pav:createdOn','pav:lastUpdatedOn'(,'.+')*\] at " \
                             "((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(doc, error):
        error_description = error
        path = utils.get_error_location(error_description)
        patches = [{
            "op": "remove",
            "path": path + "/oslc:modifiedBy"
        },
        {
            "op": "remove",
            "path": path + "/pav:createdBy"
        },
        {
            "op": "remove",
            "path": path + "/pav:createdOn"
        },
        {
            "op": "remove",
            "path": path + "/pav:lastUpdatedOn"
        }]
        return jsonpatch.JsonPatch(patches)
