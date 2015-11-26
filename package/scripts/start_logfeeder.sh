#!/bin/bash
set -e
if [ $# -ne 4 ]; then
    echo "Error: Not enough parameters. Count=$# excpected 4"
    echo "Usage: <logsearch path> <logfile> <pid file> <java_home>"
    echo "Example: $0 /opt/logfeeder /var/log/logfeeder/logfeeder.log /var/run/logfeeder/logfeeder.pid /usr/jdk64/jdk1.8.0_45"
    exit 1
fi

#path containing logfeeder e.g. /opt/logfeeder
LOGSEARCH_PATH=$1

#Logfile e.g. /var/log/solr.log
LOGFILE=$2

#pid file e.g. /var/run/solr.pid
PID_FILE=$3

JAVA_HOME=$4

if [ -f ${PID_FILE} ]; then
    PID=`cat ${PID_FILE}`
    if kill -0 $PID 2>/dev/null; then
	echo "logfeeder already running (${PID}) killing..."
	kill $PID 2>/dev/null
	sleep 5
	if kill -0 $PID 2>/dev/null; then
	    echo "logfeeder still running. Will kill process forcefully in another 10 seconds..."
	    sleep 10
	    kill -9 $PID 2>/dev/null
	    sleep 2
	fi
    fi
    if kill -0 $PID 2>/dev/null; then
	echo "ERROR: Even after all efforts to stop logfeeder, it is still running. pid=$PID. Please manually kill the service and try again."
	exit 1
    fi
fi


LOGFEEDER_JAVA_MEM="-Xmx512m"
#JMX="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.port=2098"

#Incase you want to send additional jar or configs to the logfeeder when ran as offline
#LOGFEEDER_CLI_CLASSPATH=
 
cd $LOGSEARCH_PATH
echo "Starting Logsearch..."	
$JAVA_HOME/bin/java -cp "$LOGFEEDER_CLI_CLASSPATH:/etc/logfeeder/conf:libs/*:classes:LogProcessor.jar" $LOGFEEDER_JAVA_MEM $JMX org.apache.ambari.logfeeder.LogFeeder $* >> $LOGFILE 2>&1 &	
echo $! > $PID_FILE
