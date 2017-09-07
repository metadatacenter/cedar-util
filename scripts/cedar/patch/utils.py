import re
from urllib.parse import quote


def escape(s):
    return quote(str(s), safe='')


def get_paths(data, pattern=None):
    output = set()
    walk(output, "", data)
    if pattern is not None:
        pattern = re.compile(pattern)
        output = [element for element in output if pattern.match(element)]
    return output


def walk(output, path, data):
    for k, v in data.items():
        if isinstance(v, dict):
            output.add(path + "/" + k)
            walk(output, path + "/" + k, v)
        else:
            output.add(path + "/" + k)


def get_error_location(text):
    found = ''
    try:
        found = re.search('at (/.+?)$', text).group(1)
    except AttributeError:
        found = ''
    return found


def check_argument(argname, argobj, isreq=True):
    if isreq:
        if argobj is None:
            raise Exception("The method requires the '" + argname + "' argument")


def check_argument_not_none(argname, arg):
    if arg is None:
        raise Exception("The method requires the '" + argname + "' argument")
