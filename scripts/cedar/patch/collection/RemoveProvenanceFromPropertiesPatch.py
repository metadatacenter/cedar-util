import jsonpatch
import re
from cedar.patch import utils


class RemoveProvenanceFromPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the provenance fields (i.e., 'oslc:modifiedBy','pav:createdBy'," \
                           "'pav:createdOn','pav:lastUpdatedOn' in the properties of a template field or element"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    @staticmethod
    def is_applied(error_message, doc=None):
        pattern = re.compile(
            "object instance has properties which are not allowed by the schema: " \
            "\[('.+',)*'oslc:modifiedBy','pav:createdBy','pav:createdOn','pav:lastUpdatedOn'(,'.+')*\] " \
            "at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*/properties$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
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

        parent_object, parent_path = utils.get_parent_object(doc, path)

        remove_list = ["oslc:modifiedBy", "pav:createdBy", "pav:createdOn", "pav:lastUpdateOn"]
        required_list = [item for item in parent_object.get("required") if item is not remove_list]

        patches.append({
            "op": "replace",
            "value": required_list,
            "path": parent_path + "/required"
        })

        return jsonpatch.JsonPatch(patches)
