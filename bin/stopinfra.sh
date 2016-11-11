#!/bin/bash
clear
echo ---------------------------------------------
echo Stopping CEDAR infrastructure services
echo ---------------------------------------------
echo

shopt -s expand_aliases
source $CEDAR_HOME/cedar-util/bin/profile_include.sh

killkk
stopnginx
stopmongo
stopelastic
stopkibana