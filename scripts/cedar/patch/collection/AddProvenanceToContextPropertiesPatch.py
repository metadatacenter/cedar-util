import jsonpatch
import re
from cedar.patch import utils


class AddProvenanceToContextPropertiesPatch(object):

    def __init__(self):
        self.description = "Fixes the missing provenance fields (i.e., 'oslc:modifiedBy','pav:createdBy'," \
                           "'pav:createdOn','pav:lastUpdatedOn' in the @context/properties object of a template"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile("object has missing required properties \(\[('.+',)*'oslc:modifiedBy','pav:createdBy','pav:createdOn','pav:lastUpdatedOn'(,'.+')*\]\) at /properties/@context/properties$")
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
        utils.check_argument_not_none("doc", doc)

        error_description = error
        path = utils.get_error_location(error_description)

        context_path = path[:path.rfind("/properties")]

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
            "path": context_path + "/required/-"
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
            "path": context_path + "/required/-"
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
            "path": context_path + "/required/-"
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
            "path": context_path + "/required/-"
        }]
        return jsonpatch.JsonPatch(patches)
