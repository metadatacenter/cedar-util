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
        pattern = re.compile("instance failed to match exactly one schema \(matched \d out of 4\) at ((/properties/[^/]+/items)*(/properties/[^/]+)*)*$")
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

        resource_object =  dpath.util.get(doc, self.path)

        title = resource_object.get("title") or ""
        if not title:  # if title is empty
            patch = {
                "op": "add",
                "value": "blank",
                "path": self.path + "/title"
            }
            patches.append(patch)

        description = resource_object.get("description") or ""
        if not description:
            patch = {
                "op": "add",
                "value": "blank",
                "path": self.path + "/description"
            }
            patches.append(patch)

        created_on = resource_object.get("pav:createdOn") or ""
        if not created_on:
            patch = {
                "op": "add",
                "value": None,
                "path": self.path + "/pav:createdOn"
            }
            patches.append(patch)

        created_by = resource_object.get("pav:createdBy") or ""
        if not created_by:
            patch = {
                "op": "add",
                "value": None,
                "path": self.path + "/pav:createdBy"
            }
            patches.append(patch)

        last_updated_on = resource_object.get("pav:lastUpdatedOn") or ""
        if not last_updated_on:
            patch = {
                "op": "add",
                "value": None,
                "path": self.path + "/pav:lastUpdatedOn"
            }
            patches.append(patch)

        modified_by = resource_object.get("oslc:modifiedBy") or ""
        if not modified_by:
            patch = {
                "op": "add",
                "value": None,
                "path": self.path + "/oslc:modifiedBy"
            }
            patches.append(patch)

        return patches
