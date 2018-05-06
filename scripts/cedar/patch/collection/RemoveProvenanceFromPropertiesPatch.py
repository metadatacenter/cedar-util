import jsonpatch
import re
from cedar.patch import utils


class RemoveProvenanceFromPropertiesPatch(object):

    def __init__(self):
        self.description = "Removes the provenance fields (i.e., 'oslc:modifiedBy','pav:createdBy'," \
                           "'pav:createdOn','pav:lastUpdatedOn' in the properties of a template field or element"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
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

        # Remove those provenance fields from the required list, if present
        parent_object, parent_path = utils.get_parent_object(doc, path)
        required_list = parent_object.get("required")
        if required_list is not None:
            remove_list = ["oslc:modifiedBy", "pav:createdBy", "pav:createdOn", "pav:lastUpdateOn"]
            patches.append({
                "op": "replace",
                "value": [item for item in required_list if item is not remove_list],
                "path": parent_path + "/required"
            })

        return jsonpatch.JsonPatch(patches)
