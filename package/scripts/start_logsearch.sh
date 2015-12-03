#!/bin/bash
set -e

#path containing start.jar file e.g. /opt/solr/latest/server
export LOGSEARCH_PATH=$1

#Logfile e.g. /var/log/solr.log
export LOGFILE=$2

#pid file e.g. /var/run/solr.pid
export PID_FILE=$3

export JAVA_HOME=$4

export LOGSEARCH_JAVA_MEM=$5
if [ "$LOGSEARCH_JAVA_MEM" = "" ]; then
    export LOGSEARCH_JAVA_MEM="-Xmx1g"
fi

cd $LOGSEARCH_PATH
echo "Starting Logsearch..."	
./run.sh
