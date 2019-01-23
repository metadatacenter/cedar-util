#!/usr/bin/python3
import argparse
import os
from fnmatch import fnmatch
import json


# Utility to transform CEDAR instances. It reads all the values from a source instance and fills out a target instance
# with those values. This utility can be used to update an old instance to a most recent version of the template model.
# Limitation: it only works for flat instances. It needs to be updated to work with nested elements.

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-path",
                        dest='source_path',
                        required=True,
                        nargs=1,
                        metavar=("SOURCE_PATH"),
                        help="folder with the instances that need to be transformed")
    parser.add_argument("--dest-path",
                        dest='dest_path',
                        required=True,
                        nargs=1,
                        metavar=("DESTINATION_PATH"),
                        help="folder where the transformed instances will be stored")
    parser.add_argument("--ref-instance-path",
                        dest='ref_instance_path',
                        required=True,
                        nargs=1,
                        metavar=("REFERENCE_INSTANCE"),
                        help="path of the instance that will be used as a reference to transform the source instances")
    parser.add_argument("--limit",
                        dest='limit',
                        required=False,
                        nargs=1,
                        type=int,
                        metavar=("LIMIT"),
                        help="maximum number of instances to be transformed")
    args = parser.parse_args()
    source_path = args.source_path[0]
    dest_path = args.dest_path[0]
    ref_instance_path = args.ref_instance_path[0]
    limit = args.limit[0]

    transform(source_path, dest_path, ref_instance_path, limit)


def transform(source_path, dest_path, ref_instance_path, limit):
    """
    Transforms all instances in a folder
    :param source_path:
    :param dest_path:
    :param ref_instance_path:
    :return: this function does not return anything. The transformed instances are saved to the destination path.
    """
    pattern = "*.json"
    instance_paths = []
    for path, subdirs, files in os.walk(source_path):
        for file_name in files:
            if fnmatch(file_name, pattern):
                instance_paths.append(os.path.join(path, file_name))
    # Load each instance and transform it
    count = 1;
    total_count = len(instance_paths)
    ref_instance_json = json.load(open(ref_instance_path))
    for instance_path in instance_paths:
        try:
            instance_json = json.load(open(instance_path))

            transformed_instance_path = os.path.join(dest_path, os.path.relpath(instance_path, source_path))
            transformed_instance_json = transform_instance(instance_json, ref_instance_json)

            # Save transformed instance
            if not os.path.exists(os.path.dirname(transformed_instance_path)):
                os.makedirs(os.path.dirname(transformed_instance_path))

            with open(transformed_instance_path, 'w') as output_file:
                json.dump(transformed_instance_json, output_file, indent=4)
                print("Saved instance no. " + str(count) + " (" + str(float((100 * count) / total_count)) + "%) to "
                      + transformed_instance_path)
            count += 1
            if count > limit:
                break;
        except ValueError:
            print('Decoding JSON has failed for this instance')


def transform_instance(instance_json, ref_instance_json):
    """
    It takes the values of instance_json and fills out ref_instance_json with them
    :param instance_json:
    :param ref_instance_json:
    :return: the reference instance filled out with the values from the original instance
    """
    for ref_field in ref_instance_json:
        if ref_field not in ['@context', 'schema:isBasedOn']:
            if ref_field in instance_json:
                ref_instance_json[ref_field] = instance_json[ref_field]

    # Removes the @id field to be able to post the transformed instance
    if '@id' in ref_instance_json:
        del ref_instance_json['@id']

    return ref_instance_json


if __name__ == "__main__":
    main()
