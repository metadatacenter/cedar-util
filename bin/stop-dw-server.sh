#!/bin/bash
`uname -a | grep -q 'Linux'`
if [ $? = 0 ]; then
	echo "Linux detected, using nc to stop Jetty" $1
	echo "StopMe"$'\n'"stop" | nc 127.0.0.1 $1
else
	echo "Non-linux detected, using netcat to stop Jetty" $1
	echo "StopMe"$'\n'"stop" | netcat 127.0.0.1 $1
fi