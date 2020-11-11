import copy


class PatchingEngine(object):

    def __init__(self):
        self.patches = []
        self.__solved_errors = []
        self.__unsolved_errors = []

    def add_patch(self, patch):
        self.patches.append(patch)

    def execute(self, resource, validation_callback):
        resource_copy = copy.deepcopy(resource)
        for patch in self.patches:
            resource_copy = patch.apply_patch(resource_copy)
        changed = False
        if resource != resource_copy:
            changed = True
        #is_valid = validation_callback(resource_copy)
        is_valid = True
        return changed, is_valid, resource_copy
