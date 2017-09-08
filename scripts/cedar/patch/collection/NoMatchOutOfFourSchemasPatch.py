import jsonpatch
import re
import dpath
from cedar.patch import utils


class NoMatchOutOfFourSchemasPatch(object):

    def __init__(self):
        self.description = "Fix the potential errors that trigger schema match error between 4 options:" \
                           "template field, template element, static field, or an array of fields or elements"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile("instance failed to match exactly one schema \(matched 0 out of 4\) at ((/properties/[^/]+/items)?(/properties/[^/]+)?)*/properties/[^/]+$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_patch(self, doc, error):
        utils.check_argument_not_none("doc", doc)
        error_description = error
        path = utils.get_error_location(error_description)

        user_property = self.get_user_property_object(doc, path)
        path = user_property["path"]
        user_property_object = user_property["object"]

        patches = []
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
            "path": path + "/@context"
        }
        patches.append(patch)

        property_object = user_property_object.get("properties")
        if property_object is not None:
            if utils.is_static_template_field(user_property_object):
                patch = {
                    "op": "remove",
                    "path": path + "/properties"
                }
                patches.append(patch)

        if property_object is not None:
            at_type = property_object.get("@type")
            if at_type is not None:
                one_of = at_type.get("oneOf")
                if one_of is None:
                    patch = {
                        "op": "replace",
                        "value": {
                            "oneOf": [
                                {
                                    "type": "string",
                                    "format": "uri"
                                },
                                {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "type": "string",
                                        "format": "uri"
                                    },
                                    "uniqueItems": True
                                }
                            ]
                        },
                        "path": path + "/properties/@type"
                    }
                    patches.append(patch)

        title = user_property_object.get("title") or ""
        if not title:  # if title is empty
            patch = {
                "op": "add",
                "value": "blank",
                "path": path + "/title"
            }
            patches.append(patch)

        description = user_property_object.get("description") or ""
        if not description:
            patch = {
                "op": "add",
                "value": "blank",
                "path": path + "/description"
            }
            patches.append(patch)

        created_on = user_property_object.get("pav:createdOn") or ""
        if not created_on:
            patch = {
                "op": "add",
                "value": None,
                "path": path + "/pav:createdOn"
            }
            patches.append(patch)

        created_by = user_property_object.get("pav:createdBy") or ""
        if not created_by:
            patch = {
                "op": "add",
                "value": None,
                "path": path + "/pav:createdBy"
            }
            patches.append(patch)

        last_updated_on = user_property_object.get("pav:lastUpdatedOn") or ""
        if not last_updated_on:
            patch = {
                "op": "add",
                "value": None,
                "path": path + "/pav:lastUpdatedOn"
            }
            patches.append(patch)

        modified_by = user_property_object.get("oslc:modifiedBy") or ""
        if not modified_by:
            patch = {
                "op": "add",
                "value": None,
                "path": path + "/oslc:modifiedBy"
            }
            patches.append(patch)

        schema_version = user_property_object.get("schema:schemaVersion") or ""
        if not schema_version:
            patch = {
                "op": "add",
                "value": "1.1.0",
                "path": path + "/schema:schemaVersion"
            }
            patches.append(patch)

        return jsonpatch.JsonPatch(patches)

    @staticmethod
    def get_user_property_object(doc, path):
        user_property_object = dpath.util.get(doc, path)
        items_object = user_property_object.get("items")
        if items_object:
            path = path + "/items"
            user_property_object = items_object
        return {
            "path": path,
            "object": user_property_object
        }
