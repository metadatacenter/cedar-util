#!/bin/bash
clear
echo ---------------------------------------------
echo Starting CEDAR infrastructure services
echo ---------------------------------------------
echo

mongod &
elasticsearch &
kibana &
$KEYCLOAK_HOME/bin/standalone.sh &
sudo nginx