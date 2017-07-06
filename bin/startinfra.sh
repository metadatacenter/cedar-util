#!/bin/bash
clear
echo --------------------------------------------------------------------------------
echo Starting CEDAR infrastructure services
echo --------------------------------------------------------------------------------
echo

$CEDAR_HOME/cedar-util/bin/startmongo.sh
$CEDAR_HOME/cedar-util/bin/startmysql.sh
$CEDAR_HOME/cedar-util/bin/startelastic.sh
$CEDAR_HOME/cedar-util/bin/startkibana.sh
$CEDAR_HOME/cedar-util/bin/startneo.sh
$CEDAR_HOME/cedar-util/bin/startredis.sh
$CEDAR_HOME/cedar-util/bin/startkeycloak.sh
$CEDAR_HOME/cedar-util/bin/startnginx.sh
