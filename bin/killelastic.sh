#!/bin/bash
echo ---------------------------------------------
echo Stopping Elastic Search
echo ---------------------------------------------
echo

kill `ps ax | grep "[e]lastic" | awk '{print $1}'`