import jsonpatch
import re
import dpath
from cedar.patch import utils


class NoMatchOutOfTwoSchemasPatch(object):

    def __init__(self):
        self.description = "Fix the potential errors that trigger schema match error between 2 options: template field or template element"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error_description):
        pattern = re.compile("instance failed to match exactly one schema \(matched 0 out of 2\) at ((/properties/[^/]+/items)?(/properties/[^/]+)?)*/properties/[^/]+/items$")
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

        user_property_object = dpath.util.get(doc, self.path)

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

        resource_type = user_property_object.get("@type")
        if resource_type:
            if resource_type == "https://schema.metadatacenter.org/core/TemplateField":
                ui_object = user_property_object.get("_ui")
                ui_title = ui_object.get("title") or ""
                if not ui_title:
                    patch = {
                        "op": "add",
                        "value": "Title is auto-generated by CEDAR Patch",
                        "path": self.path + "/_ui/title"
                    }
                    patches.append(patch)
                ui_description = ui_object.get("description") or ""
                if not ui_description:
                    patch = {
                        "op": "add",
                        "value": "Description is auto-generated by CEDAR Patch",
                        "path": self.path + "/_ui/description"
                    }
                    patches.append(patch)
                input_type = ui_object.get("inputType") or ""
                if not input_type:
                    patch = {
                        "op": "add",
                        "value": "textfield",
                        "path": self.path + "/_ui/inputType"
                    }
                    patches.append(patch)
            elif resource_type == "https://schema.metadatacenter.org/core/TemplateElement":
                ui_object = user_property_object.get("_ui")
                ui_title = ui_object.get("title") or ""
                if not ui_title:
                    patch = {
                        "op": "add",
                        "value": "Title is auto-generated by CEDAR Patch",
                        "path": self.path + "/_ui/title"
                    }
                    patches.append(patch)
                ui_description = ui_object.get("description") or ""
                if not ui_description:
                    patch = {
                        "op": "add",
                        "value": "Description is auto-generated by CEDAR Patch",
                        "path": self.path + "/_ui/description"
                    }
                    patches.append(patch)
                ui_order = ui_object.get("order") or ""
                if not ui_order:
                    patch = {
                        "op": "add",
                        "value": [],
                        "path": self.path + "/_ui/order"
                    }
                    patches.append(patch)
                ui_property_labels = ui_object.get("propertyLabels") or ""
                if not ui_property_labels:
                    patch = {
                        "op": "add",
                        "value": {},
                        "path": self.path + "/_ui/propertyLabels"
                    }
                    patches.append(patch)

        return patches
