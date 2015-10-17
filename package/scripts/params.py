#!/usr/bin/env python
from resource_management import *
import os
from resource_management.libraries.functions.default import default

# config object that holds the configurations declared in the -config.xml file
config = Script.get_config()

hdp_version = default("/commandParams/version", None)

# logsearch configs
#logsearch_dir = config['configurations']['logsearch-config']['logsearch_dir']
logsearch_dir = '/usr/hdp/'+hdp_version+'/logsearch'
logsearch_downloadlocation = config['configurations']['logsearch-config']['logsearch_download_location']
logsearch_numshards = str(config['configurations']['logsearch-config']['logsearch_collection_numshards'])
logsearch_repfactor = str(config['configurations']['logsearch-config']['logsearch_collection_rep_factor'])

  
#solr configs
solr_dir = config['configurations']['solr-config']['solr.dir']
solr_znode = config['configurations']['solr-config']['solr.znode']
solr_downloadlocation = config['configurations']['solr-config']['solr.download.location']
solr_cloudmode = config['configurations']['solr-config']['solr.cloudmode']

if solr_downloadlocation == 'HDPSEARCH':
  solr_dir='/opt/lucidworks-hdpsearch/solr'
  solr_bindir = solr_dir + '/bin/'
else:
  solr_bindir = solr_dir + '/latest/bin/' 


#otherconfigs
java64_home = config['hostLevelParams']['java_home']  
#get comma separated list of zookeeper hosts from clusterHostInfo
zookeeper_hosts = ",".join(config['clusterHostInfo']['zookeeper_hosts'])


#TODO: use zookeeper znode for solr instead once logsearch system.properties supports it
solr_host = config['configurations']['logsearch-config']['solr_host']
solr_port = str(config['configurations']['logsearch-config']['solr_port'])



# logsearch-env configs
logsearch_user = config['configurations']['logsearch-env']['logsearch_user']
logsearch_group = config['configurations']['logsearch-env']['logsearch_group']
logsearch_log_dir = config['configurations']['logsearch-env']['logsearch_log_dir']
logsearch_log = logsearch_log_dir+'/logsearch.log'

# store the log file for the service from the 'solr.log' property of the 'logsearch-env.xml' file
logsearch_env_content = config['configurations']['logsearch-env']['content']

#e.g. /var/lib/ambari-agent/cache/stacks/HDP/2.2/services/solr-stack/package
service_packagedir = os.path.realpath(__file__).split('/scripts')[0]


