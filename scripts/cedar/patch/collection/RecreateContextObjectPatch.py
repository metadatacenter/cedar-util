import jsonpatch
from cedar.patch import utils


class RecreateAtContextPatch(object):

    def __init__(self):
        self.description = "Fixes the incomplete namespaces in the @context object"
        self.since = "1.1.0"
        self.patbh = None

    def is_applied(self, error_description):
        return True

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc, path=None):
        paths = self.get_all_context_paths(doc)
        patches = []
        for path in paths:
            patch = {
                "op": "remove",
                "path": path
            }
            patches.append(patch)
            patch = {
                "op": "add",
                "value": {
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                    "pav": "http://purl.org/pav/",
                    "oslc": "http://open-services.net/ns/core#",
                    "schema": "http://schema.org/",
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
                "path": path
            }
            patches.append(patch)

        return patches

    def get_all_context_paths(self, doc):
        paths = ["/@context"]
        paths.extend(utils.get_paths(doc, "/properties/.+/@context$"))
        return paths
