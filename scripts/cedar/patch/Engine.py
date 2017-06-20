import utils


class Engine(object):

    def __init__(self):
        self.patches = []

    def add_patch(self, patch):
        self.patches.append(patch)

    def execute(self, template_ids, debug=False):
        patching_report = {
            "success": [],
            "failed": []
        }
        for template_id in template_ids:
            if debug:
                print("--------------------------------------------------------------------------------------")
                print(template_id)
                print("--------------------------------------------------------------------------------------")

            patched_template = utils.get_template(template_id)

            retry = False
            while True:
                if debug:
                    if retry:
                        print("RE-VALIDATING...", end="")
                    else:
                        print("VALIDATING... ", end="")
                is_valid, report = utils.validate_template(patched_template)
                if not is_valid:
                    if debug:
                        print("NOT OK")
                    patched_template = self.apply_patch(patched_template, report, debug)
                    if patched_template is None:
                        patching_report["failed"].append(template_id)
                        break
                else:
                    if debug:
                        print("OK")
                    patching_report["success"].append(template_id)
                    break
                retry = True

        return patching_report

    def apply_patch(self, template, report, debug=False):
        for message in report:
            if debug:
                print("* Fixing " + message, end="")
            for patch in self.patches:
                if patch.is_applied(message):
                    if debug:
                        print("... Success!")
                    patched_template = patch.apply(template)
                    return patched_template
            if debug:
                print("... Failed: Patch is not available!")
        return None
