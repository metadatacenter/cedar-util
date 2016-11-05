#!/bin/bash
clear
echo ---------------------------------------------
echo Stopping Keycloak Server
echo ---------------------------------------------
echo

# use [k] to prevent matching the ps + cedarssgrep itself
echo Processes:
ps ax | grep "[k]eycloak/standalone"

echo Kill them
kill `ps ax | grep "[k]eycloak/standalone" | awk '{print $1}'`