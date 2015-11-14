#!/bin/bash
set -e


#path containing logfeeder e.g. /opt/logfeeder
LOGSEARCH_PATH=$1

#Logfile e.g. /var/log/solr.log
LOGFILE=$2

#pid file e.g. /var/run/solr.pid
PID_FILE=$3

JAVA_HOME=$4

LOGFEEDER_JAVA_MEM="-Xmx512m"
#Temporarily enabling JMX so we can monitor the memory and CPU utilization of the process
JMX="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.port=2098"

#LOGFEEDER_CLI_CLASSPATH=
 
cd $LOGSEARCH_PATH
echo "Starting Logsearch..."	
$JAVA_HOME/bin/java -cp "$LOGFEEDER_CLI_CLASSPATH:/etc/logfeeder/conf:libs/*:classes:LogProcessor.jar" $LOGFEEDER_JAVA_MEM $JMX org.apache.ambari.logfeeder.LogFeeder $* >> $LOGFILE 2>&1 &	
echo $! > $PID_FILE
