#!/bin/bash
clear
echo ---------------------------------------------
echo Starting CEDAR infrastructure services
echo ---------------------------------------------
echo

mongod &
elasticsearch &
kibana &
startkk
startnginx