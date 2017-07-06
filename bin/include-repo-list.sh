#!/bin/bash
CEDAR_REPOS=( "cedar-admin-tool" "cedar-conf" "cedar-docker-build" "cedar-docker-deploy" "cedar-docs" "cedar-group-server" "cedar-keycloak-event-listener" "cedar-model-validation-library" "cedar-messaging-server" "cedar-parent" "cedar-project" "cedar-repo-server" "cedar-resource-server" "cedar-schema-server" "cedar-server-core-library" "cedar-swagger-ui" "cedar-template-editor" "cedar-template-server" "cedar-terminology-server" "cedar-user-server" "cedar-util" "cedar-valuerecommender-server" "cedar-worker-server" "cedar-submission-server" "cedar-workspace-server")

echo List of CEDAR repos:
for i in "${CEDAR_REPOS[@]}"
do
   echo "   - " $i
done