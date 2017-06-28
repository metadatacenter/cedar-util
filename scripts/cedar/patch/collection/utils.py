def is_template(resource):
    is_template = False
    resource_type = resource.get("@type")
    if resource_type:  # if exists
        is_template = resource_type == "https://schema.metadatacenter.org/core/Template"
    return is_template


def is_template_field(resource):
    is_field = False
    resource_type = resource.get("@type")
    if resource_type:  # if exists
        is_field = resource_type == "https://schema.metadatacenter.org/core/TemplateField"
    return is_field


def is_template_element(resource):
    is_element = False
    resource_type = resource.get("@type")
    if resource_type:  # if exists
        is_element = resource_type == "https://schema.metadatacenter.org/core/TemplateElement"
    return is_element


def is_static_template_field(resource):
    is_static_field = False
    resource_type = resource.get("@type")
    if resource_type:  # if exists
        is_static_field = resource_type == "https://schema.metadatacenter.org/core/StaticTemplateField"
    return is_static_field
