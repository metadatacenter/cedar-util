#!/bin/bash
echo ---------------------------------------------
echo Stopping Kibana
echo ---------------------------------------------
echo

kill `ps ax | grep "[k]ibana" | awk '{print $1}'`