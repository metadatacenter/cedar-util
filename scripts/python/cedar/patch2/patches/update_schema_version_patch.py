import dpath.util
import jsonpatch
from jsonpath_ng.ext import parse
import cedar.patch2.constants as const
import cedar.utils.general_utils as util


class UpdateSchemaVersion:

    def __init__(self, new_version):
        self.description = "Updates the schema version"
        self.target_resource_types = [const.RESOURCE_TYPE_TEMPLATE, const.RESOURCE_TYPE_TEMPLATE_ELEMENT,
                                      const.RESOURCE_TYPE_TEMPLATE_FIELD, const.RESOURCE_TYPE_TEMPLATE_INSTANCE]
        self.new_version = new_version

    def apply_patch(self, doc):
        if util.matches_target_resource_types(doc, self.target_resource_types):
            print('Applying patch: ' + type(self).__name__)
            doc = self.patch_update_schema_version(doc, self.new_version)
            return doc
        else:
            print('Patching for this resource type: ' + doc['@id'])

    @staticmethod
    def patch_update_schema_version(doc, new_version):
        jsonpath_expr = parse("$..'schema:schemaVersion'")
        target_paths = []
        for match in jsonpath_expr.find(doc):
            target_paths.append(util.jsonpath_to_xpath(str(match.full_path)))
        for target_path in target_paths:
            for result in dpath.util.search(doc, target_path, yielded=True):
                field_value = result[1]
                # Check that the field value is a string
                if isinstance(field_value, str):
                    patch = jsonpatch.JsonPatch(
                        [{"op": "replace", "path": target_path, "value": new_version}])
                    doc = patch.apply(doc)
        return doc

