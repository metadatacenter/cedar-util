#!/bin/bash
echo --------------------------------------------------------------------------------
echo Starting CEDAR $1 server
echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

java \
  -jar $CEDAR_HOME/cedar-$1-server/cedar-$1-server-application/target/cedar-$1-server-application-*.jar \
  server \
  "$CEDAR_HOME/cedar-$1-server/cedar-$1-server-application/config.yml"
echo --------------------------------------------------------------------------------
echo