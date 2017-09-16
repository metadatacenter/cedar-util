import copy
import jsonpatch


class Engine(object):

    def __init__(self):
        self.patches = []
        self.__solved_errors = []
        self.__unsolved_errors = []

    def add_patch(self, patch):
        self.patches.append(patch)

    def execute(self, template, validate_template, debug=False):
        self.__solved_errors[:] = []
        copy_template = copy.deepcopy(template)

        if debug:
            print(" INFO     | Patching the template <" + template["@id"] + ">")

        patched_template = None

        stop_trying = False
        resolvable = True
        while not stop_trying:
            is_valid, report = validate_template(copy_template)
            if is_valid:
                stop_trying = True
                resolvable = True
            else:
                output = self.__apply_patch(copy_template, report, debug)
                if output is not None:
                    copy_template = copy.deepcopy(output)
                    patched_template = output
                else:
                    stop_trying = True
                    resolvable = False
        if debug:
            if resolvable:
                if patched_template is None:
                    print(" INFO     | Template is already valid!\n")
                else:
                    print(" SUCCESS  | Template is successfully patched!\n")
            else:
                for unsolved_error in self.__unsolved_errors:
                    print(" ERROR    | Unable to fix " + unsolved_error);
                print(" FATAL    | Unable to fix the template!\n")

        return resolvable, patched_template

    def __apply_patch(self, template, report, debug=False):
        self.__unsolved_errors[:] = []
        patched_template = None
        for error_message in report:
            found_patch = False
            for patch in self.patches:
                if patch.is_applied(error_message, template) and error_message not in self.__solved_errors:
                    found_patch = True
                    patched_template = patch.apply_patch(template, error_message)
                    break

            if found_patch:
                if debug:
                    print(" PATCHED  | " + error_message)
                self.__solved_errors.append(error_message)
                break
            else:
                self.__unsolved_errors.append(error_message)

        return patched_template
