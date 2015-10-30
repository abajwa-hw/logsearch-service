#!/bin/bash
set -e


#path containing start.jar file e.g. /opt/solr/latest/server
LOGSEARCH_PATH=$1

#Logfile e.g. /var/log/solr.log
LOGFILE=$2

#pid file e.g. /var/run/solr.pid
PID_FILE=$3

JAVA_HOME=$4


cd $LOGSEARCH_PATH
echo "Starting Logsearch..."	
$JAVA_HOME/bin/java -cp 'libs/*:classes:LogSearch.jar' org.apache.ambari.logsearch.LogSearch >> $LOGFILE 2>&1 &	
echo $! > $PID_FILE

