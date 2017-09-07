import jsonpatch
import re
import dpath
from cedar.patch import utils


class AddRequiredToFieldOrElementPatch(object):

    def __init__(self):
        self.description = "Add the missing required field in a template element or field"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error_description, template=None):
        if template is None:
            pass # Just ignore

        pattern = re.compile("object has missing required properties \(\['required'\]\) at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description)
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    def get_json_patch(self, doc=None, path=None):
        utils.check_argument_not_none(doc, "The method requires the 'doc' argument")

        if self.path is None and path is None:
            raise Exception("The method requires the 'path' argument")

        if path is not None:
            self.path = path

        patches = []
        if not self.is_static_type(doc):
            user_property = self.get_all_properties(doc)
            patch = {
                "op": "add",
                "value": user_property,
                "path": self.path + "/required"
            }
            patches.append(patch)

        return patches

    def get_all_properties(self, doc):
        properties = list(dpath.util.get(doc, self.path + "/properties").keys())
        system_properties = [
            "@id",
            "@type",
            "_valueLabel",
            "pav:createdOn",
            "pav:createdBy",
            "pav:lastUpdatedOn",
            "oslc:modifiedBy"]
        return [prop for prop in properties if prop not in system_properties]

    def is_static_type(self, doc):
        type_value = dpath.util.get(doc, self.path + "/@type")
        return "StaticTemplateField" in type_value
