#!/bin/bash
clear
echo ---------------------------------------------
echo Stopping Play enabled CEDAR microservices
echo ---------------------------------------------
echo

shopt -s expand_aliases
source $CEDAR_HOME/cedar-util/bin/profile_include.sh

stopfolder
stoprepo
stopgroup
stopresource
stopschema
stoptemplate
killterminology
stopuser
killvaluerecommender
