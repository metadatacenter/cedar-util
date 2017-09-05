import argparse
from cedar.utils import getter, searcher, storer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from",
                        dest='from_server',
                        required=True,
                        nargs=2,
                        metavar=("SERVER-ADDRESS", "CEDAR-API-KEY"),
                        help="The source server that holds all the resources to copy")
    parser.add_argument("--to",
                        dest='to_server',
                        required=True,
                        nargs=2,
                        metavar=("SERVER-ADDRESS", "CEDAR-API-KEY"),
                        help="The destination server into which all the resources are copied")
    args = parser.parse_args()
    source_server_address, source_api_key = args.from_server
    target_server_address, target_api_key = args.to_server

    migrate(source_server_address, target_server_address, source_api_key, target_api_key)


def migrate(source_server_address, target_server_address, source_api_key, target_api_key):
    template_ids = get_template_ids(source_server_address, source_api_key)
    for template_id in template_ids:
        print("Copying template: " + template_id)
        template = get_template(source_server_address, source_api_key, template_id)
        store_template(target_server_address, target_api_key, template)
        print("Copying instances:")
        instance_ids = get_instance_ids(source_server_address, source_api_key, template_id)
        store_instances(target_server_address, target_api_key, instance_ids)
    print("Copying elements:")
    element_ids = get_element_ids(source_server_address, source_api_key)
    store_elements(element_ids)


def get_template_ids(server_address, api_key):
    return searcher.search_templates(server_address, api_key)


def get_element_ids(server_address, api_key):
    return searcher.search_elements(server_address, api_key)


def get_instance_ids(server_address, api_key, template_id):
    return searcher.search_instances_of(server_address, api_key, template_id)


def get_template(server_address, api_key, template_id):
    return getter.get_template(server_address, api_key, template_id)


def get_element(server_address, api_key, element_id):
    return getter.get_element(server_address, api_key, element_id)


def get_instance(server_address, api_key, instance_id):
    return getter.get_instance(server_address, api_key, instance_id)


def store_template(server_address, api_key, template):
    storer.store_template(server_address, api_key, template, import_mode=True)


def store_elements(server_address, api_key, element_ids):
    total_elements = len(element_ids)
    for counter, element_id in enumerate(element_ids, start=1):
        print_progressbar(element_id, counter, total_elements)
        element = get_element(server_address, api_key, element_id)
        store_element(server_address, api_key, element)


def store_element(server_address, api_key, element):
    storer.store_element(server_address, api_key, element, import_mode=True)


def store_instances(server_address, api_key, instance_ids):
    total_instances = len(instance_ids)
    for counter, instance_id in enumerate(instance_ids, start=1):
        print_progressbar(instance_id, counter, total_instances)
        instance = get_instance(server_address, api_key, instance_id)
        store_instance(server_address, api_key, instance)


def store_instance(server_address, api_key, instance):
    storer.store_instance(server_address, api_key, instance, import_mode=True)


def print_progressbar(resource_id, counter, total_count):
    resource_hash = extract_resource_hash(resource_id)
    percent = 100 * (counter / total_count)
    filled_length = int(percent)
    bar = "#" * filled_length + '-' * (100 - filled_length)
    print("\rCopying (%d/%d): |%s| %d%% Complete [%s]" % (counter, total_count, bar, percent, resource_hash), end='\r')


def extract_resource_hash(resource_id):
    return resource_id[resource_id.rfind('/')+1:]


if __name__ == "__main__":
    main()
