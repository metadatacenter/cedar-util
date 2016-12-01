#!/bin/bash
clear
echo ---------------------------------------------
echo Stopping Play enabled CEDAR microservices
echo ---------------------------------------------
echo

shopt -s expand_aliases
source $CEDAR_HOME/cedar-util/bin/profile_include.sh

killfolder
stoprepo
stopgroup
killresource
stopschema
killtemplate
killterminology
stopuser
killvaluerecommender
