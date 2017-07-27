#!/bin/bash
clear
echo --------------------------------------------------------------------------------
echo Stopping CEDAR infrastructure services
echo --------------------------------------------------------------------------------
echo

$CEDAR_HOME/cedar-util/bin/killkeycloak.sh
$CEDAR_HOME/cedar-util/bin/stopmongo.sh
$CEDAR_HOME/cedar-util/bin/stopelastic.sh
$CEDAR_HOME/cedar-util/bin/stopkibana.sh
$CEDAR_HOME/cedar-util/bin/stopneo.sh
$CEDAR_HOME/cedar-util/bin/killrediscommander.sh
$CEDAR_HOME/cedar-util/bin/stopredis.sh
$CEDAR_HOME/cedar-util/bin/stopmysql.sh
$CEDAR_HOME/cedar-util/bin/stopnginx.sh
