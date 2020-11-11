import jsonpatch
import re
from cedar.utils import general_utils as utils


class AddProvenanceToContextPropertiesPatch(object):

    def __init__(self):
        self.description = "Fixes the missing provenance fields (i.e., 'oslc:modifiedBy','pav:createdBy'," \
                           "'pav:createdOn','pav:lastUpdatedOn' in the @context/properties object of a template"
        self.from_version = "1.0.0"
        self.to_version = "1.1.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'oslc:modifiedBy','pav:createdBy','pav:createdOn','pav:lastUpdatedOn'(,'.+')*\]\) " \
            "at /properties/@context/properties$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        parent_path = utils.get_parent_path(path)

        patches = [{
            "op": "add",
            "value": {
                "type": "object",
                "properties": {
                    "@type": {
                        "type": "string",
                        "enum": [
                            "@id"
                        ]
                    }
                }
            },
            "path": path + "/oslc:modifiedBy"
        },
        {
            "op": "add",
            "value": "oslc:modifiedBy",
            "path": parent_path + "/required/-"
        },
        {
            "op": "add",
            "value": {
                "type": "object",
                "properties": {
                    "@type": {
                        "type": "string",
                        "enum": [
                            "@id"
                        ]
                    }
                }
            },
            "path": path + "/pav:createdBy"
        },
        {
            "op": "add",
            "value": "pav:createdBy",
            "path": parent_path + "/required/-"
        },
        {
            "op": "add",
            "value": {
                "type": "object",
                "properties": {
                    "@type": {
                        "type": "string",
                        "enum": [
                            "xsd:dateTime"
                        ]
                    }
                }
            },
            "path": path + "/pav:createdOn"
        },
        {
            "op": "add",
            "value": "pav:createdOn",
            "path": parent_path + "/required/-"
        },
        {
            "op": "add",
            "value": {
                "type": "object",
                "properties": {
                    "@type": {
                        "type": "string",
                        "enum": [
                            "xsd:dateTime"
                        ]
                    }
                }
            },
            "path": path + "/pav:lastUpdatedOn"
        },
        {
            "op": "add",
            "value": "pav:lastUpdatedOn",
            "path": parent_path + "/required/-"
        }]
        return jsonpatch.JsonPatch(patches)
