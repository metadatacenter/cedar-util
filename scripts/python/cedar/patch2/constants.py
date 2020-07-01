#
# CEDAR Constants
#

import os

# Resource types
RESOURCE_TYPE_TEMPLATE = "template"
RESOURCE_TYPE_TEMPLATE_ELEMENT = "template-element"
RESOURCE_TYPE_TEMPLATE_FIELD = "template-field"
RESOURCE_TYPE_TEMPLATE_INSTANCE = "template-instance"

# Mongo DB collections
MONGODB_TEMPLATE_COLLECTION = "templates"
MONGODB_TEMPLATE_ELEMENT_COLLECTION = "template-elements"
MONGODB_TEMPLATE_FIELD_COLLECTION = "template-fields"
MONGODB_TEMPLATE_INSTANCE_COLLECTION = "template-instances"

# Connection settings
CEDAR_SERVER_ADDRESS = "https://resource." + os.environ['CEDAR_HOST']
CEDAR_ADMIN_API_KEY = "apiKey " + os.environ['CEDAR_ADMIN_USER_API_KEY']
MONGODB_CONNECTION_STRING = "mongodb://" + os.environ['CEDAR_MONGO_ROOT_USER_NAME'] + ":" + os.environ['CEDAR_MONGO_ROOT_USER_PASSWORD'] + "@localhost:27017/admin"