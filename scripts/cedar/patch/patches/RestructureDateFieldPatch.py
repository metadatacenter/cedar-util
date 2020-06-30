import dpath.util
import jsonpatch
from jsonpath_ng.ext import parse
import cedar.constants as const

from cedar.utils import general_utils


class RestructureDateFieldPatch:

    def __init__(self):
        self.description = "Restructure the model schema for the date field, which will be now a temporal field"
        self.target_resource_types = [const.RESOURCE_TYPE_TEMPLATE, const.RESOURCE_TYPE_TEMPLATE_ELEMENT,
                                      const.RESOURCE_TYPE_TEMPLATE_FIELD]

    def apply_patch(self, doc):
        if general_utils.matches_target_resource_types(doc, self.target_resource_types):
            doc = self.patch_value_constraints(doc)
            doc = self.patch_ui(doc)
            return doc
        else:
            print('Patching skipped for this resource type: ' + doc['@id'])

    @staticmethod
    def patch_value_constraints(doc):
        jsonpath_expr = parse("$.._ui.inputType")

        target_paths = []
        for match in jsonpath_expr.find(doc):
            target_paths.append(general_utils.jsonpath_to_xpath(str(match.full_path)))

        for target_path in target_paths:
            for result in dpath.util.search(doc, target_path, yielded=True):
                if result[1] == 'date':  # Check that we are only patching 'date' fields
                    vc_path = general_utils.get_parent_path(general_utils.get_parent_path(target_path)) + "/_valueConstraints"
                    patch = jsonpatch.JsonPatch([{
                        "op": "add",
                        "path": vc_path + "/temporalType",
                        "value": "xsd:date"}
                    ])
                    doc = patch.apply(doc)
        return doc

    @staticmethod
    def patch_ui(doc):
        jsonpath_expr = parse("$.._ui.inputType")

        target_paths = []
        for match in jsonpath_expr.find(doc):
            target_paths.append(general_utils.jsonpath_to_xpath(str(match.full_path)))

        for target_path in target_paths:
            for result in dpath.util.search(doc, target_path, yielded=True):
                if result[1] == 'date':  # Check that we are only patching 'date' fields
                    parent_path = general_utils.get_parent_path(target_path)
                    patch = jsonpatch.JsonPatch(
                        [{"op": "replace", "path": target_path, "value": "temporal"},
                         {"op": "add", "path": parent_path + "/temporalGranularity", "value": "day"}])
                    doc = patch.apply(doc)
        return doc


