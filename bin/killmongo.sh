#!/bin/bash
echo ---------------------------------------------
echo Stopping MongoDB
echo ---------------------------------------------
echo

kill `ps ax | grep "[m]ongod" | awk '{print $1}'`