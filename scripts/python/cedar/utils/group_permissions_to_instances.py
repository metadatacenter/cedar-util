import os, sys
from cedar.utils import getter, updater, searcher


def main():
    # Program parameters
    server_address = "https://resource." + os.environ['CEDAR_HOST']
    template_id = sys.argv[1]
    group_id = sys.argv[2]
    api_key = "apiKey " + os.environ['CEDAR_ADMIN_USER_API_KEY']
    permission_type = sys.argv[3]

    # print("Starting search for instances of:" + template_id)
    # print("Adding permission " + permission_type + " to group: " + group_id)

    instance_ids = searcher.search_instances_of(server_address, api_key, template_id)
    for instance_id in instance_ids:
        add_group_permission_to_instance(server_address, api_key, template_id, instance_id, group_id, permission_type)


def add_group_permission_to_instance(server_address, api_key, template_id, instance_id, group_id, permission_type):
    instance_permissions = getter.get_instance_permissions(server_address, api_key, instance_id)
    group_permissions = instance_permissions['groupPermissions']
    if has_no_group_id(group_permissions, group_id):
        print("Adding a new group permission to " + instance_id)
        print("Group id: " + group_id)
        print("Template: " + template_id)
        print("-------------------------------------")
        instance_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
        updater.update_instance_permission(server_address, api_key, instance_id, instance_permissions)


def has_no_group_id(group_permissions, group_id):
    for group_permission in group_permissions:
        current_group_id = group_permission['group']['@id']
        if current_group_id == group_id:
            return False
    return True


def create_group_permission(group_id, permission_type):
    return {
        'group': {
            '@id': group_id
        },
        'permission': permission_type
    }


if __name__ == "__main__":
    main()
