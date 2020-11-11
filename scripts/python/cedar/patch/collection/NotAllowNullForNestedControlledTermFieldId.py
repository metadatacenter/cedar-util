import jsonpatch
import re
from cedar.utils import general_utils as utils


class NotAllowNullForNestedControlledTermFieldId(object):

    def __init__(self):
        self.description = "Removes the option to have a 'null' value in the @id field of a controlled-term field"
        self.from_version = "1.5.0"
        self.to_version = "1.6.0"

    def is_applied(self, error_message, doc=None):
        if not utils.is_compatible(doc, self.from_version):
            return False
        pattern = re.compile(
            "instance failed to match exactly one schema \(matched 0 out of [2|3|6]\) " \
            "at .*$")
        return pattern.match(error_message)

    def apply_patch(self, doc, error_message):
        patch = self.get_patch(error_message, doc)
        patched_doc = patch.apply(doc)
        return patched_doc

    def get_patch(self, error_message, doc=None):
        path = utils.get_error_location(error_message)

        patches = self.construct_patches_recursively(doc, path)
        return jsonpatch.JsonPatch(patches)

    def construct_patches_recursively(self, doc, root_element_path):
        patches = []

        root_element_path = self.get_proper_path(doc, root_element_path)

        patches.append({
            "op": "replace",
            "value": "string",
            "path": root_element_path + "/properties/@id/type"
        })

        properties_path = root_element_path + "/properties"
        properties_object = utils.get_json_node(doc, properties_path)
        user_fields = self.get_user_fields(properties_object)

        for user_field in user_fields:
            user_field_path = properties_path + "/" + user_field
            user_field_path = self.get_proper_path(doc, user_field_path)
            user_field_object = utils.get_json_node(doc, user_field_path)

            if utils.is_template_element(user_field_object):
                patches.extend(self.construct_patches_recursively(doc, user_field_path))
            elif utils.is_template_field(user_field_object):
                id_path = user_field_path + "/properties/@id"
                if utils.path_exists(doc, id_path):
                    patches.append({
                        "op": "replace",
                        "value": "string",
                        "path": id_path + "/type"
                    })
        return patches

    @staticmethod
    def get_proper_path(doc, root_path):
        if utils.path_exists(doc, root_path + "/items"):
            root_path = root_path + "/items"
        return root_path

    @staticmethod
    def get_user_fields(properties_object):
        exclude_list = ["@context", "@id", "@type"]
        property_names = list(properties_object.keys())
        return [item for item in property_names if item not in exclude_list]