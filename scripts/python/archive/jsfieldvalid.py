#!/usr/bin/python

# July-19-2016
# jsfieldvalid.py: Script to check CEDAR json instance for unused/un-deleted fields
#
# Partially addresses bug in CEDAR that retains deleted fields in the instance JSON: finds strings of the format
# that untitled fields are named, and deletes them and their properties from a CEDAR json instance file
# Also notifies of any fields named "untitled" for re-naming
#
# Reads from directory of files, can overwrite input or have output directory specified.
# Print debugging information option included (and to confirm deletions as they are found)

import argparse
import sys
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="JSON file or directory to process. Use absolute path for directory.",
                        required=True)
    parser.add_argument("-o", "--output", help="JSON file or directory to write. Use absolute path for directory.",
                        required=False)
    parser.add_argument("-c", "--confirm", help="Ask user for confirmations. Enter True or False", required=False)
    parser.add_argument("-p", "--u_print", help="allow printing debugging info. Enter True or False", required=False)

    args = parser.parse_args()
    file_name = args.input
    output_name = args.output
    confirmation = args.confirm
    print_option = args.u_print

    validate_fields(file_name, output_name, confirmation, print_option)


def validate_fields(file_name, output_name=None, confirmation=False, print_option=False):

    regex = "\"\w{8}\-\w{4}\-\w{4}\-\w{4}\-\w{12}\""
    regex_property = ",\s*?" + regex + "[^\]\}]*?:.*?\{.*?.*?\"enum\".*?}"
    regex_required_value = regex + "[^\{\}\[\]]*?,\n"

    if not valid_json_file(file_name, "input"):
        print("invalid json file")
        exit()
    elif print_option:
        print("File: ", file_name)

    input_file = open(file_name, 'r+')
    f = input_file.read()

    untitled = regex_search("untitled", f, True)
    if len(untitled) != 0:
        print("Find and replace unidentified fields: ", len(untitled))

    input_file.close()
    found = 0
    deleted = 0

    if print_option:
        print("SEARCHING INVALID PROPERTIES")
    result_list = regex_search(regex_property, f, True)

    if print_option:
        print("search complete")
    properties_deleted, found, deleted = delete_one(result_list, confirmation, f, found, deleted)

    if print_option:
        print("SEARCHING INVALID VALUES")
    result_list = regex_search(regex_required_value, f, False)

    if print_option:
        print("search complete")
    new_string, found, deleted = delete_one(result_list, confirmation, properties_deleted, found, deleted)

    if print_option:
        print("Number of invalid pattern occurrences found: ", found)
        if (found == deleted) or confirmation:
            print("All pattern occurrences deleted. ")
        else:
            print("Number of pattern occurrences deleted: ", deleted)

    if output_name:
        output_file = open(output_name, 'w+')
    else:
        output_file = open("/Users/kcollins/Documents/scripts/jsfieldvalid_output.json", 'w+')

    output_file.write(new_string)
    input_file.close()
    output_file.close()


def delete_one(result_list, confirmation, f, i, j, print_option=False):

    new_string = f
    for result in result_list:
        if print_option:
            print()
            print(result)
            print()
        i += 1
        if confirmation:
            new_string, j = user_confirm(re.escape(result), new_string)
        else:
            new_string, n = regex_delete(re.escape(result), new_string)
            if print_option:
                print("patterns deleted: ", n)
            j = i
    return new_string, i, j


def user_confirm(regex, f):
    j = 0
    new_string = f
    delete = input("Delete this pattern? (Y or N)")
    yes_list = ["yes", "Y", "y", "YES", "Yes"]
    if delete in yes_list:
        new_string, n = regex_delete(regex, f)
        print("deleted patterns: ", n)
        j += 1
    return new_string, j


def regex_delete(regex, input_string):
    regex = re.compile(regex, re.DOTALL | re.M)

    ret, n = re.subn(regex, "", input_string)
    return ret, n


def regex_search(regex, input_string, dotall):
    if dotall:
        search_string = re.compile(regex, re.DOTALL | re.M)
    else:
        search_string = re.compile(regex)

    result = search_string.findall(input_string)
    return result


def valid_json_file(check_file, str_check):
    if check_file.endswith(".json"):
        return True
    else:
        print("Invalid " + str_check + "file(s), try again with .json files(s)")
        sys.exit()


if __name__ == "__main__":
    main()
