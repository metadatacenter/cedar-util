#!/usr/bin/python

# July-14-2016
# jsclean.py: Utility to prepare CEDAR json instances for upload according to the CEDAR template model
#
# Takes parameters of either an input directory to iterate through or an input file, and either will rewrite input
# files or output location can be specified to leave input location unchanged.
#
# Adds template ID field to instance, deletes any instance id field so it can be reset upon upload
# Adds UI title and description fields to satisfy CEDAR requirements

import json
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--directory", help="If included, input and output are directories.", action='store_true')
    group.add_argument("-f", "--file", help="If included, input and output are files", action='store_true')
    parser.add_argument("-i", "--input", help="JSON file or directory to process. Use absolute path for directory.",
                        required=True)
    parser.add_argument("-o", "--output", help="JSON output file or directory. Use absolute path for directory.",
                        required=False)
    args = parser.parse_args()

    input_files = []
    output_files = []
    directory = args.directory
    args_file = args.file
    json_input = args.input
    json_output = args.output

    print(json_output)

    if directory:
        print("directory")
        if not os.path.exists(json_input):
            print("Input directory does not exist. Please try again.")
            sys.exit()

        input_files = directory_walk(json_input)

        # print "input files:", input_files

        if json_output:
            for i in range(len(input_files)):    # create an output file name for every input file
                output_file_name = os.path.basename(input_files[i])[:-5] + "_output" + input_files[i][-5:]
                output_files.append(os.path.join(json_output, output_file_name))
            # print "output files:", output_files
        else:
            for i in range(len(input_files)):  # each file writes to itself
                output_file_name = input_files[i]
                output_files.append(output_file_name)

    elif args_file:
        print("file")
        if valid_json_file(json_input, "input"):
            input_files.append(args.input)

        if valid_json_file(json_output, "output"):
            output_files.append(args.output)

    clean_files(input_files, output_files)


def clean_files(input_files, output_files):
    for i in range(len(input_files)):
        f = open(os.path.abspath(input_files[i]), 'r+')
        data = json.load(f)

        output = data

        keys = output.keys()
        # template ID of template instance follows
        # current template ID is "Data Element" template on staging server
        output["_templateId"] = "https://repo.staging.metadatacenter.net/templates/634324b6-ffe9-4b3d-a9bb-875aeba5144a"

        if "@id" in keys:
            del output["@id"]

        output["_ui"] = {}
        output["_ui"]["title"] = os.path.basename(input_files[i]).strip(".json")
        try:
            output["_ui"]["description"] = output["longName"]["_value"] + " publicId_" + output["publicID"]["_value"]
        except KeyError:
            output["_ui"]["description"] = output["_ui"]["title"]

        f.close()

        with open(output_files[i], 'w') as output_file:
            json.dump(output, output_file, indent=2)


def directory_walk(json_input):
    input_files = []
    for sub_dirs, dirs, files in os.walk(json_input):
        for dir_file in files:
            if valid_json_file(dir_file, "input"):
                input_files.append(os.path.join(json_input, dir_file))
    return input_files


def valid_json_file(check_file, check_str):
    if check_file.endswith(".json"):
        return True
    elif check_file == "log.txt":
        pass
    else:
        print("Invalid files in " + check_str + " directory, check all files to convert are .json files(s)")
        return False


if __name__ == "__main__":
    main()
