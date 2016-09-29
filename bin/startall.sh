#!/bin/bash
clear
echo ---------------------------------------------
echo Starting Play enabled CEDAR microservices
echo ---------------------------------------------
echo

shopt -s expand_aliases
source $CEDAR_HOME/cedar-util/bin/profile_include.sh

startfolder
startpermission
startrepo
startresource
startschema
starttemplate
startterminology
startuser
startvaluerecommender
