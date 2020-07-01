import jsonpatch
import re
from python.cedar.patch import utils


class RecreateAdditionalValuePatch(object):

    def __init__(self):
        self.description = "Fixes additional properties when having attribute-value fields in a template or element"
        self.from_version = "1.3.0"
        self.to_version = "1.4.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance type \(boolean\) does not match any allowed primitive type " \
            "\(allowed: \['object'\]\) " \
            "at (/.+)?/additionalProperties$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        path = utils.get_error_location(error_message)
        patches = [{
            "op": "remove",
            "path": path
        },
        {
            "op": "add",
            "value": {
                "type": "object",
                "properties": {
                    "@value": {
                        "type": [
                            "string",
                            "null"
                        ]
                    },
                    "@type": {
                        "type": "string",
                        "format": "uri"
                    }
                },
                "required": [
                  "@value"
                ],
                "additionalProperties": False
            },
            "path": path
        }]
        return jsonpatch.JsonPatch(patches)
