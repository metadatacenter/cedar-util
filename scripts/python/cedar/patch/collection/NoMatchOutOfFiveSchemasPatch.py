import jsonpatch
import re
from python.cedar.patch import utils


class NoMatchOutOfFiveSchemasPatch(object):

    def __init__(self):
        self.description = "Fix the potential errors that trigger schema match error between 5 options:" \
                           "single-valued template field, multi-valued template field, static-valued template field, " \
                           "template element or an array of fields or elements"
        self.from_version = "1.1.0"
        self.to_version = "1.2.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance failed to match exactly one schema \(matched 0 out of 5\) " \
            "at ((/properties/[^/]+/items)?(/properties/[^/]+)?)*/properties/[^/]+$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    def get_patch(self, error_message, doc=None):
        path = utils.get_error_location(error_message)

        user_property_paths = []
        self.collect_user_property_paths(user_property_paths, doc, path)

        patches = []
        for user_property_path in user_property_paths:
            self.collect_patches(patches, doc, user_property_path)

        return jsonpatch.JsonPatch(patches)

    def collect_user_property_paths(self, user_property_paths, doc, property_path):
        property_object = utils.get_json_node(doc, property_path)
        if property_object is not None:
            properties_path = property_path + "/properties"
            user_property_path = property_path
            if "items" in property_object:
                properties_path = property_path + "/items/properties"
                user_property_path = property_path + "/items"

            user_property_paths.append(user_property_path)

            properties_object = utils.get_json_node(doc, properties_path)
            if properties_object is not None:
                for propname in list(properties_object.keys()):
                    property_path = properties_path + "/" + propname
                    property_object = utils.get_json_node(doc, property_path)
                    if property_object is not None:
                        if "items" in property_object:
                            property_path = property_path + "/items"
                            property_object = utils.get_json_node(doc, property_path)
                        if utils.is_template_element(property_object):
                            self.collect_user_property_paths(user_property_paths, doc, property_path)
                        elif utils.is_template_field(property_object) or utils.is_static_template_field(property_object):
                            user_property_paths.append(property_path)

    def collect_patches(self, patches, doc, path):
        # Fix @context
        context_path = path + "/@context"
        context_object = utils.get_json_node(doc, context_path)
        if context_object is not None:
            patch = {
                "op": "replace",
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
                "path": context_path
            }
            patches.append(patch)

        user_property_object = utils.get_json_node(doc, path)
        properties_object = user_property_object.get("properties")

        # Recreate the required array for template element or template field
        required_path = path + "/required"
        required_object = utils.get_json_node(doc, required_path)
        if required_object is not None or required_object:
            if utils.is_template_element(user_property_object):
                patch = {
                    "op": "remove",
                    "path": path + "/required"
                }
                patches.append(patch)
                patch = {
                    "op": "add",
                    "value": self.get_required_properties_for_template_element(user_property_object),
                    "path": path + "/required"
                }
                patches.append(patch)
            elif utils.is_template_field(user_property_object):
                patch = {
                    "op": "remove",
                    "path": path + "/required"
                }
                patches.append(patch)
                patch = {
                    "op": "add",
                    "value": self.get_required_properties_for_template_field(user_property_object),
                    "path": path + "/required"
                }
                patches.append(patch)

        # Remove pav and oslc prefixes from properties/@context/properties for template element
        if utils.is_template_element(user_property_object):
            if properties_object is not None:
                pav_path = path + "/properties/@context/properties/pav"
                pav_object = utils.get_json_node(doc, pav_path)
                if pav_object is not None:
                    patch = {
                        "op": "remove",
                        "path": pav_path
                    }
                    patches.append(patch)
                oslc_path = path + "/properties/@context/properties/oslc"
                oslc_object = utils.get_json_node(doc, oslc_path)
                if oslc_object is not None:
                    patch = {
                        "op": "remove",
                        "path": oslc_path
                    }
                    patches.append(patch)

        # Remove patternProperties from properties/@context for template element and field
        if utils.is_template_element(user_property_object) or utils.is_template_field(user_property_object):
            if properties_object is not None:
                pattern_properties_path = path + "/properties/@context/patternProperties"
                pattern_properties_object = utils.get_json_node(doc, pattern_properties_path)
                if pattern_properties_object is not None:
                    patch = {
                        "op": "remove",
                        "path": pattern_properties_path
                    }
                    patches.append(patch)

        # Remove properties object from static template field
        if utils.is_static_template_field(user_property_object):
            if properties_object is not None:
                patch = {
                    "op": "remove",
                    "path": path + "/properties"
                }
                patches.append(patch)

        # Fix the oneOf object
        if utils.is_template_element(user_property_object) or utils.is_template_field(user_property_object):
            if properties_object is not None:
                at_type = properties_object.get("@type")
                if at_type is not None:
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

        # Rename _valueLabel to rdfs:label
        if utils.is_template_element(user_property_object) or utils.is_template_field(user_property_object):
            if properties_object is not None:
                value_label = properties_object.get("_valueLabel")
                if value_label is not None:
                    patch = {
                        "op": "remove",
                        "path": path + "/properties/_valueLabel"
                    }
                    patches.append(patch)
                    patch = {
                        "op": "add",
                        "value": {
                            "type": [
                                "string",
                                "null"
                            ]
                        },
                        "path": path + "/properties/rdfs:label"
                    }
                    patches.append(patch)

        # Remove provenance from properties
        if utils.is_template_element(user_property_object) or utils.is_template_field(user_property_object):
            if properties_object is not None:
                modified_by = properties_object.get("oslc:modifiedBy")
                if modified_by is not None:
                    patch = {
                        "op": "remove",
                        "path": path + "/properties/oslc:modifiedBy"
                    }
                    patches.append(patch)

                created_by = properties_object.get("pav:createdBy")
                if created_by is not None:
                    patch = {
                        "op": "remove",
                        "path": path + "/properties/pav:createdBy"
                    }
                    patches.append(patch)

                created_on = properties_object.get("pav:createdOn")
                if created_on is not None:
                    patch = {
                        "op": "remove",
                        "path": path + "/properties/pav:createdOn"
                    }
                    patches.append(patch)

                last_updated_on = properties_object.get("pav:lastUpdatedOn")
                if last_updated_on is not None:
                    patch = {
                        "op": "remove",
                        "path": path + "/properties/pav:lastUpdatedOn"
                    }
                    patches.append(patch)

        # Move title out from _ui, if exists, and rename it to schema:name
        ui_object = user_property_object.get("_ui")
        if ui_object:
            ui_title = ui_object.get("title")
            if ui_title is not None:
                patch = {
                    "op": "move",
                    "from": path + "/_ui/title",
                    "path": path + "/schema:name"
                }
                patches.append(patch)
            else:
                schema_name = user_property_object.get("schema:name")
                if schema_name is None:
                    patch = {
                        "op": "add",
                        "value": "Title is auto-generated by CEDAR Patch",
                        "path": path + "/schema:name"
                    }
                    patches.append(patch)

        # Move description out from _ui, if exists, and rename it to schema:description
        if ui_object:
            ui_description = ui_object.get("description")
            if ui_description is not None:
                patch = {
                    "op": "move",
                    "from": path + "/_ui/description",
                    "path": path + "/schema:description"
                }
                patches.append(patch)
            else:
                schema_description = user_property_object.get("schema:description")
                if schema_description is None:
                    patch = {
                        "op": "add",
                        "value": "Description is auto-generated by CEDAR Patch",
                        "path": path + "/schema:description"
                    }
                    patches.append(patch)

        # Add missing fields in the _ui
        if ui_object:
            if utils.is_template_field(user_property_object):
                input_type = ui_object.get("inputType") or ""
                if not input_type:
                    patch = {
                        "op": "add",
                        "value": "textfield",
                        "path": path + "/_ui/inputType"
                    }
                    patches.append(patch)
            elif utils.is_template_element(user_property_object):
                ui_object = user_property_object.get("_ui")
                ui_order = ui_object.get("order") or ""
                if not ui_order:
                    patch = {
                        "op": "add",
                        "value": [],
                        "path": path + "/_ui/order"
                    }
                    patches.append(patch)
                ui_property_labels = ui_object.get("propertyLabels") or ""
                if not ui_property_labels:
                    patch = {
                        "op": "add",
                        "value": {},
                        "path": path + "/_ui/propertyLabels"
                    }
                    patches.append(patch)

        # Add missing fields in the document root
        title = user_property_object.get("title") or ""
        if not title:  # if title is empty
            patch = {
                "op": "add",
                "value": "Schema title is auto-generated by CEDAR Patch",
                "path": path + "/title"
            }
            patches.append(patch)

        description = user_property_object.get("description") or ""
        if not description:
            patch = {
                "op": "add",
                "value": "Schema description is auto-generated by CEDAR Patch",
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
                "value": "1.3.0",
                "path": path + "/schema:schemaVersion"
            }
            patches.append(patch)

        # Fix the requirement for having the @value (for the template field) and @id (for the template element)
        if properties_object is not None:
            if utils.is_template_element(user_property_object):
                value_object = properties_object.get("@value")
                if value_object is not None:
                    patch = {
                        "op": "remove",
                        "path": path + "/properties/@value"
                    }
                    patches.append(patch)
                id_object = properties_object.get("@id")
                if id_object is None:
                    patch = {
                        "op": "add",
                        "value": {
                            "type": "string",
                            "format": "uri"
                        },
                        "path": path + "/properties/@id"
                    }
                    patches.append(patch)
            elif utils.is_template_field(user_property_object):
                value_object = properties_object.get("@value")
                if value_object is None:
                    patch = {
                        "op": "add",
                        "value": {
                            "type": [
                                "string",
                                "null"
                            ]
                        },
                        "path": path + "/properties/@value"
                    }
                    patches.append(patch)
                id_object = properties_object.get("@id")
                if id_object is not None:
                    patch = {
                        "op": "remove",
                        "path": path + "/properties/@id"
                    }
                    patches.append(patch)
                    
        # Rearrange the required list for @context of the properties field
        if utils.is_template_element(user_property_object) or utils.is_template_field(user_property_object):
            if properties_object is not None:
                context_object = properties_object.get("@context")
                if context_object is not None:
                    context_properties_object = context_object.get("properties")
                    patch = {
                        "op": "replace",
                        "value": self.get_user_properties(context_properties_object),
                        "path": path + "/properties/@context/required"
                    }
                    patches.append(patch)

        # Add rdfs:label in the template field properties, if missing
        if utils.is_template_field(user_property_object):
            if properties_object is not None:
                rdfs_label_property = properties_object.get("rdfs:label")
                if rdfs_label_property is None:
                    patch = {
                        "op": "add",
                        "value": {
                            "type": [
                                "string",
                                "null"
                            ]
                        },
                        "path": path + "/properties/rdfs:label"
                    }
                    patches.append(patch)

    def get_required_properties_for_template_element(self, element_object):
        user_properties = self.get_user_properties(element_object.get("properties"))
        required_properties = ["@context", "@id"]
        required_properties.extend(user_properties)
        return required_properties

    def get_required_properties_for_template_field(self, field_object):
        user_properties = self.get_user_properties(field_object.get("properties"))
        required_properties = ["@value"]
        required_properties.extend(user_properties)
        return required_properties

    @staticmethod
    def get_user_properties(properties_object):
        exclude_list = ["@context", "@id", "@value", "@type", "xsd", "schema", "pav", "oslc", "pav:createdOn",
                        "pav:createdBy", "pav:lastUpdatedOn", "oslc:modifiedBy", "_valueLabel"]
        property_names = list(properties_object.keys())
        return [item for item in property_names if item not in exclude_list]
