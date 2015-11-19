#!/bin/bash
set -e


#path containing start.jar file e.g. /opt/solr/latest/server
LOGSEARCH_PATH=$1

#Logfile e.g. /var/log/solr.log
LOGFILE=$2

#pid file e.g. /var/run/solr.pid
PID_FILE=$3

JAVA_HOME=$4

LOGSEARCH_JAVA_MEM="-Xmx1g"
#Temporarily enabling JMX so we can monitor the memory and CPU utilization of the process
JMX="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.port=3098"
#LOGSEARCH_CLI_CLASSPATH=

cd $LOGSEARCH_PATH
echo "Starting Logsearch..."	
$JAVA_HOME/bin/java -cp '$LOGSEARCH_CLI_CLASSPATH:/etc/logsearch/conf:libs/*:classes:LogSearch.jar' $LOGSEARCH_JAVA_MEM $JMX org.apache.ambari.logsearch.LogSearch >> $LOGFILE 2>&1 &	
echo $! > $PID_FILE

