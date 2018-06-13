from cedar.utils import getter, updater


def add_group_permission_to_template(server_address, api_key, template_id, group_id, permission_type):
    template_permissions = getter.get_template_permissions(server_address, api_key, template_id)
    template_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
    updater.update_template_permission(server_address, api_key, template_id, template_permissions)


def add_group_permission_to_element(server_address, api_key, element_id, group_id, permission_type):
    element_permissions = getter.get_element_permissions(server_address, api_key, element_id)
    element_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
    updater.update_element_permission(server_address, api_key, element_id, element_permissions)


def add_group_permission_to_field(server_address, api_key, field_id, group_id, permission_type):
    field_permissions = getter.get_instance_permissions(server_address, api_key, field_id)
    field_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
    updater.update_field_permission(server_address, api_key, field_id, field_permissions)


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
