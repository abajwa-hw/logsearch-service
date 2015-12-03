#!/bin/bash
set -e
if [ $# -lt 4 ]; then
    echo "Error: Not enough parameters. Count=$# excpected 4 or more"
    echo "Usage: <logfeeder path> <logfile> <pid file> <java_home> [java_mem]"
    echo "Example: $0 /opt/logfeeder /var/log/logfeeder/logfeeder.log /var/run/logfeeder/logfeeder.pid /usr/jdk64/jdk1.8.0_45 -Xmx512m"
    exit 1
fi

#!/bin/bash
set -e

#path containing start.jar file e.g. /opt/solr/latest/server
export LOGFEEDER_PATH=$1

#Logfile e.g. /var/log/solr.log
export LOGFILE=$2

#pid file e.g. /var/run/solr.pid
export PID_FILE=$3

export JAVA_HOME=$4

export LOGFEEDER_JAVA_MEM=$5
if [ "$LOGFEEDER_JAVA_MEM" = "" ]; then
    export LOGFEEDER_JAVA_MEM="-Xmx512m"
fi

cd $LOGFEEDER_PATH
echo "Starting Logfeeder logfile=$LOGFILE, PID_FILE=$PID_FILE, JAVA_HOME=$JAVA_HOME, MEM=$LOGFEEDER_JAVA_MEM ..."	
./run.sh
