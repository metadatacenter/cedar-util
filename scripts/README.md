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
usage: cedar-validator.py [-h] [-s {local,staging,production}]
                          [-t {template,element,field,instance}]
                          [--lookup FILENAME] [--limit LIMIT]
                          [--validation-apikey CEDAR-API-KEY]
                          [--mongodb-connection DBCONN]
                          [--input-mongodb DBNAME] [--input-file FILENAME]

optional arguments:
  -h, --help            show this help message and exit
  -s {local,staging,production}, --server {local,staging,production}
                        the type of CEDAR server
  -t {template,element,field,instance}, --type {template,element,field,instance}
                        the type of CEDAR resource
  --lookup FILENAME     an input file containing a list of resource
                        identifiers to validate
  --limit LIMIT         the maximum number of resources to validate
  --validation-apikey CEDAR-API-KEY
                        the API key used to access the CEDAR validation
                        service
  --mongodb-connection DBCONN
                        set the MongoDB admin connection URI to perform
                        administration operations
  --input-mongodb DBNAME
                        set the MongoDB database name to get the resources to
                        validate
  --input-file FILENAME
                        an input file containing the resource to patch
```

**Example usage**:

Validate all the templates in the staging server by giving the script the access to the MongoDB storage
```buildoutcfg
$ python cedar-validator.py -s staging -t template --validation-apikey="apiKey 1234567890" --mongodb-connection="mongodb://[username]:[password]@localhost:27017/admin" --input-mongodb=cedar
```

Validate all the templates in the staging server that are listed in the text file. You need to list the complete template id, e.g., https://repo.metadatacenter.org/templates/dbb6450b-4c5e-5290-9420-fcc624b457b4
```buildoutcfg
$ python cedar-validator.py -s staging -t template --validation-apikey="apiKey 1234567890" --lookup=templates.txt
```



### Patch Resources

```buildoutcfg
usage: cedar-patch.py [-h] [-s {local,staging,production}]
                      [-t {all,template,element,field,instance}]
                      [--lookup FILENAME] [--limit LIMIT]
                      [--output-dir DIRNAME] [--mongodb-connection DBCONN]
                      [--output-mongodb DBNAME] [--commit] [--revert]
                      [--model-version VERSION] [--keep-unresolved] [--debug]
                      [--apikey CEDAR-API-KEY]

optional arguments:
  -h, --help            show this help message and exit
  -s {local,staging,production}, --server {local,staging,production}
                        the type of CEDAR server
  -t {all,template,element,field,instance}, --type {all,template,element,field,instance}
                        the type of CEDAR resource
  --lookup FILENAME     an input file containing a list of resource
                        identifiers to patch
  --limit LIMIT         the maximum number of resources to patch
  --output-dir DIRNAME  set the output directory to store the patched
                        resources
  --mongodb-connection DBCONN
                        set the MongoDB admin connection URI to perform
                        administration operations
  --output-mongodb DBNAME
                        set the MongoDB database name to store the patched
                        resources
  --commit              commit the integration of the patched resources to the
                        CEDAR system
  --revert              revert the integration of the patched resources from
                        the CEDAR system
  --model-version VERSION
                        set the CEDAR model version of the patched resources
  --keep-unresolved     include the unresolved resources as part of the output
  --debug               print the debugging messages
  --apikey CEDAR-API-KEY
```

**Example usage**:

Patch all the templates in the production server and set the output to the `/tmp` directory
```buildoutcfg
$ python cedar-patch.py --server production --type template --apikey="apiKey 1234567890" --output-dir="/tmp"
```

Patch all the templates in the production server and set the output to a MongoDB database called `cedar-patch`. Additionally, we would like also to update the model version to "1.3.0"
```buildoutcfg
$ python cedar-patch.py --server production --type template --apikey="apiKey 1234567890" --mongodb-connection="mongodb://admin:adminpass@localhost:27017/admin" --output-mongodb="cedar-patch" --model-version="1.3.0" 
```

Patch the first 100 elements in the staging server
```buildoutcfg
$ python cedar-patch.py --server staging --type element --apikey="apiKey 1234567890" --output-dir="/tmp" --limit 100 
```

Patch all the templates specified by the `template.txt`
```buildoutcfg
$ python cedar-patch.py --server staging --type element --apikey="apiKey 1234567890" --output-dir="/tmp" --lookup="template.txt" 
```

Patch all the resources in the production server and commit the changes to the real production database
```buildoutcfg
$ python cedar-patch.py --server production --type all --apikey="apiKey 1234567890" --mongodb-connection="mongodb://admin:mypass@localhost:27017/admin" --output-mongodb="cedar-patch" --model-version="1.3.0" --commit
```

Revert all the patched results from the production database
```buildoutcfg
$ python cedar-patch.py --server production --mongodb-connection="mongodb://admin:mypass@localhost:27017/admin" --output-mongodb="cedar-patch" --revert
```

### Copy Resources

```buildoutcfg
usage: cedar-migrate.py [-h] --from SERVER-ADDRESS CEDAR-API-KEY --to
                        SERVER-ADDRESS CEDAR-API-KEY [--include-instances]

optional arguments:
  -h, --help            show this help message and exit
  --from                the source server
  --to                  the destination server
  --include-instances   copy all the template instances as well
```

**Example usage**:

Copy all the resources from the CEDAR staging server to a local server (Note: use the *resource.** sub-domain of the server)
```buildoutcfg
python cedar-migrate.py --from https://resource.staging.metadatacenter.org "apiKey 1234567890" --to https://resource.metadatacenter.orgx "apiKey abcdefghij" --include-instances
```
