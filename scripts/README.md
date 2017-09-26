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
                          CEDAR-API-KEY

positional arguments:
  CEDAR-API-KEY         the API key used to access the CEDAR resource server

optional arguments:
  -h, --help            show this help message and exit
  -s, --server          the type of CEDAR server. The options are {local,staging,production}
  -t, --type            the type of CEDAR resource. The options are {template,element,field,instance}
  --lookup FILENAME     an input file containing a list of resource identifiers to validate
  --limit LIMIT         the maximum number of resources to validate
```

**Example usage**:

Validate all the templates in the staging server
```buildoutcfg
$ python cedar-validator.py --server staging --type template "apiKey 1234567890"
```

### Patch Resources

```buildoutcfg
usage: cedar-patch.py [-h] [-s {local,staging,production}]
                      [-t {template,element,field,instance}]
                      [--lookup FILENAME] [--limit LIMIT]
                      [--output-dir DIRNAME] [--output-mongodb DBCONN]
                      [--model-version VERSION] [--keep-unresolved] [--debug]
                      CEDAR-API-KEY

positional arguments:
  CEDAR-API-KEY         the API key used to access the CEDAR resource server

optional arguments:
  -h, --help            show this help message and exit
  -s, --server          the type of CEDAR server. The options are {local,staging,production}
  -t, --type            the type of CEDAR resource. The options are {template,element,field,instance}
  --lookup FILENAME     an input file containing a list of resource identifiers to patch
  --limit LIMIT         the maximum number of resources to patch
  --output-dir DIRNAME  set the output directory to store the patched resources
  --output-mongodb DBCONN
                        set the MongoDB connection URI to store the patched resources
  --model-version VERSION
                        set the CEDAR model version of the patched resources
  --keep-unresolved     include the unresolved resources as part of the output
  --debug               print the debugging messages
```

**Example usage**:

Patch all the templates in the production server and set the output to the `/tmp` directory
```buildoutcfg
$ python cedar-patch.py --server production --type template "apiKey 1234567890" --output-dir=/tmp
```

Patch all the templates in the production server and set the output to a MongoDB database called `cedar-patch` (see the Troubleshooting section to prepare a MongoDB database)
```buildoutcfg
$ python cedar-patch.py --server production --type template "apiKey 1234567890" --output-mongodb=mongodb://myuser:mypass@localhost:27017/cedar-patch
```

Patch the first 100 elements in the staging server
```buildoutcfg
$ python cedar-patch.py --server staging --type element "apiKey 1234567890" --limit 100 --output-dir=/tmp
```

Patch all the templates specified by the `template.txt`
```buildoutcfg
$ python cedar-patch.py --server staging --type element "apiKey 1234567890" --lookup=template.txt --output-dir=/tmp
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
python cedar-migrate.py --from https://resource.staging.metadatacenter.net "apiKey 1234567890" --to https://resource.metadatacenter.orgx "apiKey abcdefghij" --include-instances
```

## Troubleshooting

You need to create a new MongoDB database and set the proper roles to the user that will enable the script to store the patched resources.

1. Open a terminal and login to MongoDB
```buildoutcfg
$ mongo -u <YourAdminUser> --authenticationDatabase admin -p
```

2. Create a role that will have the privilege list all the databases
```buildoutcfg
>> use admin
>> db.runCommand({ createRole: "listDatabases",
      privileges: [
         { resource: { cluster : true }, actions: ["listDatabases"]}
      ],
      roles: []
   })
```

3. Create another role that will have the privilege to drop the `patch` database
```buildoutcfg
>> use cedar-patch
>> db.runCommand({ createRole: "dropDatabase",
      privileges: [
         { resource: { db: "cedar-patch", collection: "" }, actions: ["dropDatabase"]}
      ],
      roles: []
   })
```

4. Create a new user with some roles and additionally we will also grant a permission to list the databases in the `admin` store
```buildoutcfg
>> use cedar-patch
>> db.createUser({
   	  user: "myuser",
  	  pwd: "mypass",
   	  roles: [ "readWrite”, “dropDatabase” ]
   })
>> db.grantRolesToUser(
      "myuser",
      [
         { role: "listDatabases", db: "admin" }
      ]
   )
```
