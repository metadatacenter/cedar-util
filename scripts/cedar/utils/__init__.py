__all__ = [
    'get_server_address',
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
