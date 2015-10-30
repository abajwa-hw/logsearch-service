#!/bin/bash
set -e


#path containing logfeeder e.g. /opt/logfeeder
LOGSEARCH_PATH=$1

#Logfile e.g. /var/log/solr.log
LOGFILE=$2

#pid file e.g. /var/run/solr.pid
PID_FILE=$3

JAVA_HOME=$4

 
cd $LOGSEARCH_PATH
echo "Starting Logsearch..."	
$JAVA_HOME/bin/java -cp 'libs/*:classes:LogProcessor.jar' org.apache.ambari.logfeeder.LogFeeder >> $LOGFILE 2>&1 &	
echo $! > $PID_FILE

