#!/bin/bash

#Path to solr install dir e.g. /opt/solr
SOLR_PATH=$1

#Logfile e.g. /var/log/solr.log
LOGFILE=$2

#pid file e.g. /var/run/solr.pid
PID_FILE=$3

#path containing start.jar file e.g. /opt/solr/latest/server
START_PATH=$4

#list of zookeeper hosts e.g.  pregion-shared03.cloud.hortonworks.com,pregion-shared02.cloud.hortonworks.com,pregion-shared01.cloud.hortonworks.com
#ZOOKEEPER_HOSTS=$5

#dir containing solr.in.sh
SOLR_IN_PATH=$5

#dir containing solr.xml
SOLR_DATA_DIR=$6

echo "SOLR_IN_PATH: $SOLR_IN_PATH"  >> $LOGFILE	
echo "SOLR_DATA_DIR: $SOLR_DATA_DIR"  >> $LOGFILE	
 

#start Solr if not already started from $START_PATH dir
cd $START_PATH
#OUTPUT=`./solr start -cloud -z $ZOOKEEPER_HOSTS -noprompt`
OUTPUT=`SOLR_INCLUDE=$SOLR_IN_PATH/solr.in.sh ./solr start -cloud -noprompt -s $SOLR_DATA_DIR`
	
echo "Starting Solr Cloud..." >> $LOGFILE	
echo "$OUTPUT" >> $LOGFILE	

#PID=`echo $OUTPUT | sed -e 's/.*pid=\(.*\)).*/\1/'`
#echo $PID > $PID_FILE
#echo "Started pid $PID"	 >> $LOGFILE	


