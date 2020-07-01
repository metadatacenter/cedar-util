import dpath.util
import jsonpatch
import re
from jsonpath_ng.ext import parse
import cedar.patch2.constants as const
import cedar.utils.general_utils as util


class AddMissingColonToDatetimePatch:

    def __init__(self):
        self.description = "Fixes the missing colon in the offset of pav:createdOn and pav:lastUpdatedOn values"
        self.target_resource_types = [const.RESOURCE_TYPE_TEMPLATE, const.RESOURCE_TYPE_TEMPLATE_ELEMENT,
                                      const.RESOURCE_TYPE_TEMPLATE_FIELD, const.RESOURCE_TYPE_TEMPLATE_INSTANCE]

    def apply_patch(self, doc):
        if util.matches_target_resource_types(doc, self.target_resource_types):
            print('Applying patch: ' + type(self).__name__)
            doc = self.patch_missing_colon_datetime(doc)
            return doc
        else:
            print('Patching skipped for this resource type: ' + doc['@id'])

    @staticmethod
    def patch_missing_colon_datetime(doc):
        jsonpath_expr1 = parse("$..'pav:createdOn'")
        jsonpath_expr2 = parse("$..'pav:lastUpdatedOn'")
        target_paths = []
        for match in jsonpath_expr1.find(doc):
            target_paths.append(util.jsonpath_to_xpath(str(match.full_path)))
        for match in jsonpath_expr2.find(doc):
            target_paths.append(util.jsonpath_to_xpath(str(match.full_path)))

        for target_path in target_paths:
            for result in dpath.util.search(doc, target_path, yielded=True):
                field_value = result[1]
                # Check that the field value is a string and that the last for characters of the string are numbers
                if isinstance(field_value, str) and re.compile('.*[0-9]{4}$').match(field_value) is not None:
                    patched_value = field_value[:-2] + ":" + field_value[-2:]
                    patch = jsonpatch.JsonPatch(
                        [{"op": "replace", "path": target_path, "value": patched_value}])
                    doc = patch.apply(doc)
        return doc
