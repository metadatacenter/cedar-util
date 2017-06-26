import jsonpatch
import re
import dpath
from cedar.patch import utils


class NoSchemaMatchPatch(object):

    def __init__(self):
        self.description = "Fill the empty title or description that triggers the schema match error"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error_description):
        pattern = re.compile("instance failed to match exactly one schema \(matched \d out of 4\) at ((/properties/[^/]+/items)?(/properties/[^/]+)?)*/properties/[^/]+$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc, path=None):
        if self.path is None and path is None:
            raise Exception("The method required a 'path' location")

        if path is not None:
            self.path = path

        patches = []

        user_property_object = self.get_user_property_object(doc)

        patch = {
            "op": "replace",
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
            "path": self.path + "/@context"
        }
        patches.append(patch)

        title = user_property_object.get("title") or ""
        if not title:  # if title is empty
            patch = {
                "op": "add",
                "value": "blank",
                "path": self.path + "/title"
            }
            patches.append(patch)

        description = user_property_object.get("description") or ""
        if not description:
            patch = {
                "op": "add",
                "value": "blank",
                "path": self.path + "/description"
            }
            patches.append(patch)

        created_on = user_property_object.get("pav:createdOn") or ""
        if not created_on:
            patch = {
                "op": "add",
                "value": None,
                "path": self.path + "/pav:createdOn"
            }
            patches.append(patch)

        created_by = user_property_object.get("pav:createdBy") or ""
        if not created_by:
            patch = {
                "op": "add",
                "value": None,
                "path": self.path + "/pav:createdBy"
            }
            patches.append(patch)

        last_updated_on = user_property_object.get("pav:lastUpdatedOn") or ""
        if not last_updated_on:
            patch = {
                "op": "add",
                "value": None,
                "path": self.path + "/pav:lastUpdatedOn"
            }
            patches.append(patch)

        modified_by = user_property_object.get("oslc:modifiedBy") or ""
        if not modified_by:
            patch = {
                "op": "add",
                "value": None,
                "path": self.path + "/oslc:modifiedBy"
            }
            patches.append(patch)

        return patches

    def get_user_property_object(self, doc):
        user_property_object = dpath.util.get(doc, self.path)
        items_object = user_property_object.get("items")
        if items_object:
            self.path = self.path + "/items"
            user_property_object = items_object
        return user_property_object
