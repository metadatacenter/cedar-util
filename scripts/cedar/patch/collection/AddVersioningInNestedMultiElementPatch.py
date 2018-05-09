import jsonpatch
import re
from cedar.patch import utils


class AddVersioningInNestedMultiElementPatch(object):

    def __init__(self):
        self.description = "Add versioning in deep nested multi-elements"
        self.from_version = "1.3.0"
        self.to_version = "1.4.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance failed to match exactly one schema \(matched 0 out of 2\) " \
            "at ((/properties/[^/]+/items)?(/properties/[^/]+)?)*/properties/[^/]+/items$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message)
        patched_doc = patch.apply(doc)
        return patched_doc

    def get_patch(self, error_message, doc=None):
        path = utils.get_error_location(error_message)

        user_property_paths = [path]
        self.collect_user_property_paths(user_property_paths, doc, path)

        patches = []
        for user_property_path in user_property_paths:
            self.collect_patches(patches, user_property_path)

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

    @staticmethod
    def collect_patches(patches, path):
        patch = [{
                "op": "add",
                "value": "http://purl.org/ontology/bibo/",
                "path": path + "/@context/bibo"
            },
            {
                "op": "add",
                "value": "0.0.1",
                "path": path + "/pav:version"
            },
            {
                "op": "add",
                "value": "bibo:draft",
                "path": path + "/bibo:status"
            }]
        patches.extend(patch);
