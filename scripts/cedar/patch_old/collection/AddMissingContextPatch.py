import jsonpatch
import re
from cedar.patch import utils


class AddMissingContextPatch(object):

    def __init__(self):
        self.description = "Fixes the missing @context object of a template, element or field"
        self.from_version = "1.2.0"
        self.to_version = "1.3.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "object has missing required properties " \
            "\(\[('.+',)*'@context'(,'.+')*\]\) " \
            "at /")
        return pattern.match(error_message) and \
               (utils.is_template(doc) or utils.is_template_element(doc) or utils.is_template_field(doc))

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(error_message, doc=None):
        patches = [{
            "op": "add",
            "value": {
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "pav": "http://purl.org/pav/",
                "oslc": "http://open-services.net/ns/core#",
                "schema": "http://schema.org/",
                "schema:name": {
                  "@type": "xsd:string"
                },
                "schema:description": {
                  "@type": "xsd:string"
                },
                "pav:createdOn": {
                  "@type": "xsd:dateTime"
                },
                "pav:createdBy": {
                  "@type": "@id"
                },
                "pav:lastUpdatedOn": {
                  "@type": "xsd:dateTime"
                },
                "oslc:modifiedBy": {
                  "@type": "@id"
                }
            },
            "path": "/@context"
        }]
        return jsonpatch.JsonPatch(patches)


