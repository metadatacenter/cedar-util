#!/bin/bash
#-verbose:class \
java \
  -Dkeycloak.config.path="$CEDAR_HOME/keycloak.json" \
  -DSTOP.PORT=$2 -DSTOP.KEY="StopMe" \
  -jar $CEDAR_HOME/cedar-$1-server/cedar-$1-server-application/target/cedar-$1-server-application-*.jar \
  server \
  "$CEDAR_HOME/cedar-$1-server/cedar-$1-server-application/config.yml"