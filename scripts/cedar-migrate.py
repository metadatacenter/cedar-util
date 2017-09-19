import argparse
from cedar.utils import getter, searcher, storer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from",
                        dest='from_server',
                        required=True,
                        nargs=2,
                        metavar=("SERVER-ADDRESS", "CEDAR-API-KEY"),
                        help="the source server")
    parser.add_argument("--to",
                        dest='to_server',
                        required=True,
                        nargs=2,
                        metavar=("SERVER-ADDRESS", "CEDAR-API-KEY"),
                        help="the destination server")
    parser.add_argument("--include-instances",
                        dest="include_instances",
                        default=False,
                        action="store_true",
                        help="copy all the template instances as well")
    args = parser.parse_args()
    source_server_address, source_api_key = args.from_server
    target_server_address, target_api_key = args.to_server
    include_instances = args.include_instances

    migrate(source_server_address, target_server_address, source_api_key, target_api_key, include_instances)


def migrate(source_server_address, target_server_address, source_api_key, target_api_key, include_instances):
    template_ids = get_template_ids(source_server_address, source_api_key)
    for template_counter, template_id in enumerate(template_ids, start=1):
        template = get_template(source_server_address, source_api_key, template_id)
        print(" INFO     | Copying template %s (%d/%d)" % (get_id(template), template_counter, len(template_ids)))
        store_template(target_server_address, target_api_key, template)

        if include_instances:
            instance_ids = get_instance_ids(source_server_address, source_api_key, template_id)
            for counter, instance_id in enumerate(instance_ids, start=1):
                instance = get_instance(source_server_address, source_api_key, instance_id)
                show_instance_copying_progressbar(instance_id, counter, len(instance_ids))
                store_instance(target_server_address, target_api_key, instance)

    element_ids = get_element_ids(source_server_address, source_api_key)
    for element_counter, element_id in enumerate(element_ids, start=1):
        element = get_element(source_server_address, source_api_key, element_id)
        print(" INFO     | Copying element %s (%d/%d)" % (get_id(element), element_counter, len(element_ids)))
        store_element(target_server_address, target_api_key, element)


def get_template_ids(server_address, api_key):
    print(" INFO     | Collecting all the templates... ", end="")
    templates = searcher.search_templates(server_address, api_key)
    print(len(templates), " templates found")
    return templates


def get_element_ids(server_address, api_key):
    print(" INFO     | Collecting all the elements... ", end="")
    elements = searcher.search_elements(server_address, api_key)
    print(len(elements), " elements found")
    return elements


def get_instance_ids(server_address, api_key, template_id):
    print(" INFO     | Collecting all the corresponding instances...", end="\r")
    return searcher.search_instances_of(server_address, api_key, template_id)


def get_template(server_address, api_key, template_id):
    return getter.get_template(server_address, api_key, template_id)


def get_element(server_address, api_key, element_id):
    return getter.get_element(server_address, api_key, element_id)


def get_instance(server_address, api_key, instance_id):
    return getter.get_instance(server_address, api_key, instance_id)


def store_template(server_address, api_key, template):
    storer.store_template(server_address, api_key, template, import_mode=True)


def store_element(server_address, api_key, element):
    storer.store_element(server_address, api_key, element, import_mode=True)


def store_instance(server_address, api_key, instance):
    storer.store_instance(server_address, api_key, instance, import_mode=True)


def show_instance_copying_progressbar(resource_id, counter, total_count):
    resource_hash = extract_resource_hash(resource_id)
    percent = 100 * (counter / total_count)
    filled_length = int(percent)
    bar = "#" * filled_length + '-' * (100 - filled_length)
    if counter < total_count:
        print("\r PROGRESS | Copying instances (%d/%d): |%s| %d%% Complete [%s]"
              % (counter, total_count, bar, percent, resource_hash), end="\r")
    else:
        print("\r PROGRESS | Copying instances (%d/%d): |%s| %d%% Complete [%s]"
              % (counter, total_count, bar, percent, resource_hash))


def extract_resource_hash(resource_id):
    return resource_id[resource_id.rfind('/')+1:]


def get_id(resource):
    return resource.get("@id")


if __name__ == "__main__":
    main()
