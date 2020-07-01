# Administration Scripts

## Module structure

All the scripts are written for Python 3.x

```buildoutcfg
cedar
+-- patch                   : the module for model-updater
    +--- collection         : a patch collection for the model-updater
         +-- *Patch.py
         +--- ...
+-- utils                   : some utility methods to interact with the CEDAR server
    +--- getter.py          : Get a CEDAR resource (i.e., template/element/instance) via a GET request
    +--- remover.py         : Remove a CEDAR resource (i.e., template/element/instance) via a DELETE request
    +--- searcher.py        : Search a CEDAR resource (i.e., template/element/instance) by specifying the search keywords
    +--- storer.py          : Create a CEDAR resource (i.e., template/element/instance) via a POST request
    +--- updater.py         : Update a CEDAR resource (i.e., template/element/instance) via a PUT request
    +--- validator.py       : Validate a CEDAR resource (i.e., template/element/instance)
```

**Example usage**:
```
from cedar.utils import getter, storer, validator
```

## Executable programs

### Validate Resources

```buildoutcfg
usage: cedar-validator.py [-h] [-t {template,element,field,instance}]
                          [--input-list FILENAME] [--input-json FILENAME]
                          [--input-mongodb DBNAME] [--limit LIMIT]

optional arguments:
  -h, --help            show this help message and exit
  -t {template,element,field,instance}, --type {template,element,field,instance}
                        the type of CEDAR resource
  --input-list FILENAME
                        an input file containing a list of resource
                        identifiers to validate
  --input-json FILENAME
                        an input file containing the JSON document to validate
  --input-mongodb DBNAME
                        the name of MongoDB database where resources are
                        located
  --limit LIMIT         the maximum number of resources to validate (useful
                        when --input-mongodb is used)
```

**Example usage**:

Validate all the templates stored in a MongoDB database
```buildoutcfg
$ python cedar-validator.py -t template --input-mongodb=cedar
```

Validate all the elements where their ids are listed in a text file
```buildoutcfg
$ python cedar-validator.py -t element --input-list=elements.txt
```

Validate a field specified in a JSON file
```buildoutcfg
$ python cedar-validator.py -t instance --input-list=field.json
```

### Patch Resources

```buildoutcfg
usage: cedar-patch.py [-h] [-t {template,element,field}]
                      [--input-json FILENAME] [--input-mongodb DBNAME]
                      [--filter FILENAME] [--limit LIMIT]
                      [--output-dir DIRNAME] [--output-mongodb DBNAME]
                      [--debug]

optional arguments:
  -h, --help            show this help message and exit
  -t {template,element,field}, --type {template,element,field}
                        the type of CEDAR resource
  --input-json FILENAME
                        an input file containing the resource to patch
  --input-mongodb DBNAME
                        set the MongoDB database where resources are located
  --filter FILENAME     an input file containing a list of resource
                        identifiers to patch
  --limit LIMIT         the maximum number of resources to patch
  --output-dir DIRNAME  set the output directory to store the patched
                        resources
  --output-mongodb DBNAME
                        set the MongoDB database name to store the patched
                        resources
  --debug               print the debugging messages
```

**Example usage**:

Patch all the templates and set the output to the `/tmp` directory
```buildoutcfg
$ python cedar-patch.py -t template --input-mongodb=cedar --output-dir=/tmp
```

Patch all the templates and set the output to a MongoDB database called `cedar-patch`
```buildoutcfg
$ python cedar-patch.py -t template --input-mongodb=cedar --output-mongodb=cedar-patch 
```

Patch the first 100 elements and set the output to both a MongoDB database and the `/tmp` directory
```buildoutcfg
$ python cedar-patch.py -t element --input-mongodb=cedar --output-dir=/tmp --output-mongodb=cedar-patch --limit 100 
```

Patch all the fields filtered by the `fields.txt`
```buildoutcfg
$ python cedar-patch.py -t field --input-mongodb=cedar --filter=fields.txt --output-dir=/tmp
```
