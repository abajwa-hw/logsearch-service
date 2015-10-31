#!/usr/bin/env python
from resource_management import *
import glob

# config object that holds the status related configurations declared in the -env.xml file
config = Script.get_config()

#solr pid file
solr_piddir = config['configurations']['solr-env']['stack_piddir']
solr_port = config['configurations']['solr-config']['solr.port']
solr_pidfile = format("{solr_piddir}/solr-{solr_port}.pid")


#logsearch pid file
logsearch_pid_dir = config['configurations']['logsearch-env']['logsearch_pid_dir']
logsearch_pid_file = format("{logsearch_pid_dir}/logsearch.pid")

#logfeeder pid file
logfeeder_pid_dir = config['configurations']['logfeeder-env']['logfeeder_pid_dir']
logfeeder_pid_file = format("{logfeeder_pid_dir}/logfeeder.pid")
