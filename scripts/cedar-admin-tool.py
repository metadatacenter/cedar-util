from cedar.utils import getter, updater


def add_group_permission_to_template(api_key, server_address, template_id, group_id, permission_type):
    template_permissions = getter.get_template_permissions(api_key, server_address, template_id)
    template_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
    updater.update_template_permission(api_key, server_address, template_id, template_permissions)


def add_group_permission_to_element(api_key, server_address, element_id, group_id, permission_type):
    element_permissions = getter.get_element_permissions(api_key, server_address, element_id)
    element_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
    updater.update_element_permission(api_key, server_address, element_id, element_permissions)


def add_group_permission_to_field(api_key, server_address, field_id, group_id, permission_type):
    field_permissions = getter.get_instance_permissions(api_key, server_address, field_id)
    field_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
    updater.update_field_permission(api_key, server_address, field_id, field_permissions)


def add_group_permission_to_instance(api_key, server_address, instance_id, group_id, permission_type):
    instance_permissions = getter.get_instance_permissions(api_key, server_address, instance_id)
    instance_permissions['groupPermissions'].append(create_group_permission(group_id, permission_type))
    updater.update_instance_permission(api_key, server_address, instance_id, instance_permissions)


def create_group_permission(group_id, permission_type):
    return {
        'group': {
            'id': group_id
        },
        'permission': permission_type
    }
