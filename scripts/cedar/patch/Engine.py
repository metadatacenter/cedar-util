from cedar.patch import utils


class Engine(object):

    def __init__(self):
        self.patches = []

    def add_patch(self, patch):
        self.patches.append(patch)

    def execute(self, template, debug=False):
        if debug:
            print("--------------------------------------------------------------------------------------")
            print(template["@id"])
            print("--------------------------------------------------------------------------------------")

        patched_template = template

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
                    return False
            else:
                if debug:
                    print("OK")
                return True
            retry = True

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