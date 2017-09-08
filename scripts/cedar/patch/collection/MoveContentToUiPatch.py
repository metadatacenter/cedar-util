import jsonpatch
import re
from cedar.patch import utils


class MoveContentToUiPatch(object):

    def __init__(self):
        self.description = "Move _content object to the _ui field"
        self.from_version = None
        self.to_version = "1.1.0"
        self.path = None

    def is_applied(self, error, doc=None):
        utils.check_argument('error', error, isreq=True)
        utils.check_argument('doc', doc, isreq=False)

        error_description = error
        pattern = re.compile("object instance has properties which are not allowed by the schema: \['_content'\] at (/properties/[^/]+)*/properties$")
        if pattern.match(error_description):
            self.path = utils.get_error_location(error_description) + "/_content"
            return True
        else:
            return False

    def apply(self, doc, path=None):
        patch = self.get_json_patch(doc, path)
        patched_doc = jsonpatch.JsonPatch(patch).apply(doc)
        return patched_doc

    @staticmethod
    def get_patch(doc, error):
        error_description = error
        path = utils.get_error_location(error_description) + "/_content"
        ui_content_path = path[:path.rfind('/properties')] + "/_ui/_content"
        patches = [{
            "op": "move",
            "from": path,
            "path": ui_content_path
        }]
        return jsonpatch.JsonPatch(patches)
