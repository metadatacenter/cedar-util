from cedar.utils import searcher, getter, updater


def main():
    # Program parameters
    server_address = ""
    template_id = ""
    group_id = ""
    api_key = ""
    permission_type = ""

    instance_ids = searcher.search_instances_of(server_address, api_key, template_id)
    for instance_id in instance_ids:
        add_group_permission_to_instance(server_address, api_key, instance_id, group_id, permission_type)


def add_group_permission_to_instance(server_address, api_key, instance_id, group_id, permission_type):
    instance_permissions = getter.get_instance_permissions(server_address, api_key, instance_id)
    instance_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
    updater.update_instance_permission(server_address, api_key, instance_id, instance_permissions)


def create_group_permission(group_id, permission_type):
    return {
        'group': {
            'id': group_id
        },
        'permission': permission_type
    }


if __name__ == "__main__":
    main()
