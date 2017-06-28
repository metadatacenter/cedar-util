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
    +--- downloader.py      : Get a template/element/instance using a specific ID
    +--- finder.py          : Query and get the meta-information about templates/elements/instancea
    +--- validator.py       : Validate a template/element/instance
```

Example usage:
```
from cedar.utils import downloader
from cedar.patch.collection import *
```

## Executable programs

### model-validator

```buildoutcfg
usage: cedar-validator.py [-h] [-s {local,staging,production}]
                          [-t {template,element,field,instance}]
                          [--limit LIMIT]
                          apiKey

positional arguments:
  apiKey                The API key used to query the CEDAR resource server

optional arguments:
  -h, --help            show this help message and exit
  -s {local,staging,production}, --server {local,staging,production}
                        The type of CEDAR server
  -t {template,element,field,instance}, --type {template,element,field,instance}
                        The type of CEDAR resource
  --limit LIMIT         The maximum number of resources to validate

```

Example usage:

Validate all the templates in the staging server
```buildoutcfg
$ python cedar-validator.py --server staging --type template "<CEDAR-API-KEY>"

```

### model-updater

```buildoutcfg
usage: cedar-patch.py [-h] [-s {local,staging,production}]
                      [-t {template,element,field,instance}] [--limit LIMIT]
                      [--debug]
                      apiKey

positional arguments:
  apiKey                The API key used to query the CEDAR resource server

optional arguments:
  -h, --help            show this help message and exit
  -s {local,staging,production}, --server {local,staging,production}
                        The type of CEDAR server
  -t {template,element,field,instance}, --type {template,element,field,instance}
                        The type of CEDAR resource
  --limit LIMIT         The maximum number of resources to validate
  --debug               Enter debug mode
```

Example usage:

Patch all the templates in the production server
```buildoutcfg
$ python cedar-patch.py --server production --type template "<CEDAR-API-KEY>"
```
Note that the script will not make any data change to the server but it will run the updating workflow to apply the
corresponding patches based on the error report returned by the model-validator