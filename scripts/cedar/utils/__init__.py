import json


__all__ = [
    'get_server_address',
    'to_json_string'
]


def get_server_address(alias):
    address = "http://localhost"
    if alias == 'local':
        address = "https://resource.metadatacenter.orgx"
    elif alias == 'staging':
        address = "https://resource.staging.metadatacenter.net"
    elif alias == 'production':
        address = "https://resource.metadatacenter.net"
    return address


def to_json_string(obj, pretty=True):
    if pretty:
        return json.dumps(obj, indent=2, sort_keys=True)
    else:
        return json.dumps(obj)