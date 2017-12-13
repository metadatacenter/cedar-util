import copy


class Engine(object):

    def __init__(self):
        self.patches = []
        self.__solved_errors = []
        self.__unsolved_errors = []

    def add_patch(self, patch):
        self.patches.append(patch)

    def execute(self, resource, validation_callback, debug=False):
        self.__solved_errors[:] = []
        copy_resource = copy.deepcopy(resource)

        if debug:
            print(" INFO     | Patching the resource " + resource["@id"])

        patched_resource = None

        stop_trying = False
        resolvable = True
        while not stop_trying:
            try:
                is_valid, report = validation_callback(copy_resource)
                if is_valid:
                    stop_trying = True
                    resolvable = True
                else:
                    output = self.__apply_patch(copy_resource, report, debug)
                    if output is not None:
                        copy_resource = copy.deepcopy(output)
                        patched_resource = output
                    else:
                        stop_trying = True
                        resolvable = False
            except KeyError as error:
                print(" ERROR    | Object not found at " + str(error));
                raise error
        if debug:
            if resolvable:
                if patched_resource is None:
                    print(" INFO     | Resource is already valid!\n")
                else:
                    print(" SUCCESS  | Resource is successfully patched!\n")
            else:
                for unsolved_error in self.__unsolved_errors:
                    print(" ERROR    | Unable to fix " + unsolved_error);
                print(" FATAL    | Unable to fix the resource!\n")

        return resolvable, patched_resource

    def __apply_patch(self, resource, report, debug=False):
        self.__unsolved_errors[:] = []
        patched_resource = None
        for error_message in report:
            found_patch = False
            for patch in self.patches:
                if patch.is_applied(error_message, resource) and error_message not in self.__solved_errors:
                    found_patch = True
                    patched_resource = patch.apply_patch(resource, error_message)
                    break

            if found_patch:
                if debug:
                    print(" PATCHED  | " + error_message)
                self.__solved_errors.append(error_message)
                break
            else:
                self.__unsolved_errors.append(error_message)

        return patched_resource
