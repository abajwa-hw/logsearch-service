#!/bin/bash
set -e


#path containing logfeeder e.g. /opt/logfeeder
LOGSEARCH_PATH=$1

#Logfile e.g. /var/log/solr.log
LOGFILE=$2

#pid file e.g. /var/run/solr.pid
PID_FILE=$3

JAVA_HOME=$4

 
PID_DIR=$(dirname "$PID_FILE")

#Create pid dir if it does not exist
if [ ! -d "$PID_DIR" ]
then
	echo "Creating PID_DIR: $PID_DIR"
	mkdir -p $PID_DIR
fi

#start Solr if not already started from $START_PATH dir
if [ ! -f "$PID_FILE" ]
then
	cd $LOGSEARCH_PATH
	echo "Starting Logsearch..."	
	$JAVA_HOME/bin/java -cp 'libs/*:classes:LogProcessor.jar' org.apache.ambari.logfeeder.LogFeeder >> $LOGFILE 2>&1 &	
	echo $! > $PID_FILE
fi
