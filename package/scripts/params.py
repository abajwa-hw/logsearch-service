#!/usr/bin/env python
from resource_management import *
import os
from resource_management.libraries.functions.default import default

def get_port_from_url(address):
  if not is_empty(address):
    return address.split(':')[-1]
  else:
    return address
    
# config object that holds the configurations declared in the -config.xml file
config = Script.get_config()

hdp_version = default("/commandParams/version", None)

#e.g. /var/lib/ambari-agent/cache/stacks/HDP/2.3/services/LOGSEARCH/package
service_packagedir = os.path.realpath(__file__).split('/scripts')[0]

#shared configs
java64_home = config['hostLevelParams']['java_home']  
#get comma separated list of zookeeper hosts from clusterHostInfo
zookeeper_hosts = ",".join(config['clusterHostInfo']['zookeeper_hosts'])
cluster_name=str(config['clusterName'])


#TODO: pass all collectors
#if 'metrics_collector_hosts' in config['clusterHostInfo']:
#  metrics_collector_hosts = ",".join(config['clusterHostInfo']['metrics_collector_hosts'])
#else:
#  metrics_collector_hosts = ''

#for now just pick first collector
if 'metrics_collector_hosts' in config['clusterHostInfo']:
  metrics_collector_hosts = str(config['clusterHostInfo']['metrics_collector_hosts'][0])
  metrics_collector_port = str(get_port_from_url(config['configurations']['ams-site']['timeline.metrics.service.webapp.address']))
else:
  metrics_collector_hosts = ''
  metrics_collector_port = ''

####################################
#Smart Config
####################################
smart_solr_memory = config['configurations']['alpha-smart-config']['solr_memory']
smart_solr_datadir = config['configurations']['alpha-smart-config']['solr_datadir']

#####################################
#Solr configs
#####################################

# Only supporting HDPsearch and SolrCloud mode - so hardcode those options
solr_cloudmode='true'
solr_downloadlocation='HDPSEARCH'
#solr_cloudmode = config['configurations']['solr-config']['solr.cloudmode']
#solr_downloadlocation = config['configurations']['solr-config']['solr.download.location']
#solr_dir = config['configurations']['solr-config']['solr.dir']

solr_znode = config['configurations']['solr-config']['solr.znode']
solr_port = config['configurations']['solr-env']['solr.port']
solr_min_mem = format(config['configurations']['solr-config']['solr.minmem'])
solr_max_mem = format(config['configurations']['solr-config']['solr.maxmem'])
solr_instance_count = len(config['clusterHostInfo']['logsearch_solr_hosts'])
logsearch_solr_conf = config['configurations']['solr-config']['logsearch.solr.conf']
logsearch_solr_datadir = format(config['configurations']['solr-config']['logsearch.solr.datadir'])
logsearch_solr_data_resources_dir = os.path.join(logsearch_solr_datadir,'resources')
logsearch_service_logs_max_retention = config['configurations']['logsearch-config']['logsearch_service_logs_max_retention']
logsearch_audit_logs_max_retention = config['configurations']['logsearch-config']['logsearch_audit_logs_max_retention']
logsearch_app_max_mem = config['configurations']['logsearch-config']['logsearch_app_max_mem']

logsearch_auth_file_enable = config['configurations']['logsearch-config']['logsearch_auth_file_enable']
logsearch_auth_ldap_enable = config['configurations']['logsearch-config']['logsearch_auth_ldap_enable']
logsearch_auth_simple_enable = config['configurations']['logsearch-config']['logsearch_auth_simple_enable']

audit_logs_collection_splits_interval_mins = config['configurations']['logsearch-config']['audit_logs_collection_split_interval_mins']
service_logs_collection_splits_interval_mins = config['configurations']['logsearch-config']['service_logs_collection_split_interval_mins']


zookeeper_port=default('/configurations/zoo.cfg/clientPort', None)
#get comma separated list of zookeeper hosts from clusterHostInfo
index = 0 
zookeeper_quorum=""
for host in config['clusterHostInfo']['zookeeper_hosts']:
  zookeeper_quorum += host + ":"+str(zookeeper_port)
  index += 1
  if index < len(config['clusterHostInfo']['zookeeper_hosts']):
    zookeeper_quorum += ","

if solr_downloadlocation == 'HDPSEARCH':
  solr_dir='/opt/lucidworks-hdpsearch/solr'
  solr_bindir = solr_dir + '/bin'
  cloud_scripts=solr_dir+'/server/scripts/cloud-scripts'  
else:
  solr_bindir = solr_dir + '/latest/bin' 
  cloud_scripts=solr_dir+'/latest/server/scripts/cloud-scripts'


solr_user = config['configurations']['solr-env']['solr.user']
solr_group = config['configurations']['solr-env']['solr.group']
solr_log_dir = config['configurations']['solr-env']['solr.log.dir']
solr_log = solr_log_dir+'/solr-install.log'

solr_piddir = config['configurations']['solr-env']['solr_pid_dir']
solr_pidfile = format("{solr_piddir}/solr-{solr_port}.pid")

solr_env_content = config['configurations']['solr-env']['content']

solr_xml_content = config['configurations']['solr-xml-env']['content']

solr_log4j_content = config['configurations']['solr-log4j-env']['content']

solr_zoo_content = config['configurations']['solr-zoo-env']['content']

solr_sh_content = config['configurations']['solr-sh']['content']


#####################################
#Logsearch configs
#####################################

logsearch_downloadlocation = config['configurations']['logsearch-env']['logsearch_download_location']
if logsearch_downloadlocation == 'RPM':
  logsearch_dir = '/usr/hdp/'+hdp_version+'/logsearch'
else:  
  logsearch_dir = config['configurations']['logsearch-env']['logsearch_dir']



logsearch_downloadlocation = config['configurations']['logsearch-env']['logsearch_download_location']
logsearch_collection_service_logs = default('/configurations/logsearch-config/logsearch_collection_service_logs', 'hadoop_logs')
logsearch_collection_audit_logs = default('/configurations/logsearch-config/logsearch_collection_audit_logs', 'audit_logs')
logsearch_numshards_config = config['configurations']['logsearch-config']['logsearch_collection_numshards']

if logsearch_numshards_config > 0:
  logsearch_numshards = str(logsearch_numshards_config)
else:
  logsearch_numshards = format(str(solr_instance_count))

logsearch_repfactor = str(config['configurations']['logsearch-config']['logsearch_collection_rep_factor'])

solr_collection_service_logs = default('/configurations/logsearch-config/solr_collection_service_logs', 'hadoop_logs')
solr_collection_audit_logs = default('/configurations/logsearch-config/solr_collection_audit_logs', 'audit_logs')

solr_audit_logs_use_ranger = default('/configurations/logsearch-config/solr_audit_logs_use_ranger', 'false')
solr_audit_logs_url = ''

if solr_audit_logs_use_ranger:
  #In Ranger, this contain the /zkNode also
  ranger_audit_solr_zookeepers = default('/configurations/ranger-admin-site/ranger.audit.solr.zookeepers', None)
  #TODO: ranger property already has zk node appended. We need to remove it.
  #For now, let's assume it is going to be URL
  solr_audit_logs_url = default('/configurations/ranger-admin-site/ranger.audit.solr.urls', solr_audit_logs_url)
else:
  solr_audit_logs_zk_quorum = default('/configurations/logsearch-config/solr_audit_logs_zk_quorum', None)
  solr_audit_logs_zk_node = default('/configurations/logsearch-config/solr_audit_logs_zk_node', None)

  solr_audit_logs_zk_node = format(solr_audit_logs_zk_node)
  solr_audit_logs_zk_quorum = format(solr_audit_logs_zk_quorum)

  if not(solr_audit_logs_zk_quorum):
    solr_audit_logs_zk_quorum=zookeeper_quorum
  if not(solr_audit_logs_zk_node):
    solr_audit_logs_zk_node=solr_znode
      

# logsearch-env configs
logsearch_user = config['configurations']['logsearch-env']['logsearch_user']
logsearch_group = config['configurations']['logsearch-env']['logsearch_group']
logsearch_log_dir = config['configurations']['logsearch-env']['logsearch_log_dir']
logsearch_log = logsearch_log_dir+'/logsearch.out'

# store the log file for the service from the 'solr.log' property of the 'logsearch-env.xml' file
logsearch_env_content = config['configurations']['logsearch-env']['content']
logsearch_service_logs_solrconfig_content = config['configurations']['logsearch-service_logs-solrconfig']['content']
logsearch_audit_logs_solrconfig_content = config['configurations']['logsearch-audit_logs-solrconfig']['content']
logsearch_app_log4j_content = config['configurations']['logsearch-app-log4j']['content']

#Log dirs
ambari_server_log_dir = '/var/log/ambari-server'
ambari_agent_log_dir = '/var/log/ambari-agent'
knox_log_dir = '/var/log/knox'

metrics_collector_log_dir = default('/configurations/ams-env/metrics_collector_log_dir', '/var/log')
metrics_monitor_log_dir = default('/configurations/ams-env/metrics_monitor_log_dir', '/var/log')


atlas_log_dir = default('/configurations/atlas-env/metadata_log_dir', '/var/log/atlas')
accumulo_log_dir = default('/configurations/accumulo-env/accumulo_log_dir', '/var/log/accumulo')
falcon_log_dir = default('/configurations/falcon-env/falcon_log_dir','/var/log/falcon')
hbase_log_dir = default('/configurations/hbase-env/hbase_log_dir','/var/log/hbase')
hdfs_log_dir_prefix = default('/configurations/hadoop-env/hdfs_log_dir_prefix','/var/log/hadoop')
hive_log_dir = default('/configurations/hive-env/hive_log_dir','/var/log/hive')
kafka_log_dir = default('/configurations/kafka-env/kafka_log_dir','/var/log/kafka')
oozie_log_dir = default('/configurations/oozie-env/oozie_log_dir','/var/log/oozie')
ranger_usersync_log_dir = default('/configurations/ranger-env/ranger_usersync_log_dir', '/var/log/ranger/usersync')
ranger_admin_log_dir = default('/configurations/ranger-env/ranger_admin_log_dir', '/var/log/ranger/admin')
ranger_kms_log_dir = default('/configurations/kms-env/kms_log_dir', '/var/log/ranger/kms')
storm_log_dir = default('/configurations/storm-env/storm_log_dir','/var/log/storm')
yarn_log_dir_prefix = default('/configurations/yarn-env/yarn_log_dir_prefix','/var/log/hadoop')
mapred_log_dir_prefix = default('/configurations/mapred-env/mapred_log_dir_prefix','/var/log/hadoop')
zk_log_dir = default('/configurations/zookeeper-env/zk_log_dir','/var/log/zookeeper')


#####################################
#Logfeeder configs
#####################################

logfeeder_downloadlocation = config['configurations']['logfeeder-env']['logfeeder_download_location']
if logfeeder_downloadlocation == 'RPM':
  logfeeder_dir = '/usr/hdp/'+hdp_version+'/logfeeder'
else:  
  logfeeder_dir = config['configurations']['logfeeder-env']['logfeeder_dir']

logfeeder_downloadlocation = config['configurations']['logfeeder-env']['logfeeder_download_location']
  



# logfeeder-config configs

solr_service_logs_enable = default('/configurations/logfeeder-config/solr_service_logs_enable',True)
solr_audit_logs_enable = default('/configurations/logfeeder-config/solr_audit_logs_enable',True)

kafka_broker_list = default('/configurations/logfeeder-config/kafka_broker_list', '')
kafka_security_protocol= default('/configurations/logfeeder-config/kafka_security_protocol', '')
kafka_kerberos_service_name=default('/configurations/logfeeder-config/kafka_kerberos_service_name', '')

kafka_service_logs_enable = default('/configurations/logfeeder-config/kafka_service_logs_enable',False)
kafka_audit_logs_enable = default('/configurations/logfeeder-config/kafka_audit_logs_enable',False)
kafka_topic_service_logs = default('/configurations/logfeeder-config/kafka_topic_service_logs','service_logs')
kafka_topic_audit_logs = default('/configurations/logfeeder-config/kafka_topic_audit_logs','audit_logs')


# logfeeder-env configs
logfeeder_user = config['configurations']['logfeeder-env']['logfeeder_user']
logfeeder_group = config['configurations']['logfeeder-env']['logfeeder_group']
logfeeder_log_dir = config['configurations']['logfeeder-env']['logfeeder_log_dir']
logfeeder_log = logfeeder_log_dir+'/logfeeder.out'
logfeeder_max_mem = config['configurations']['logfeeder-env']['logfeeder_max_mem']
logfeeder_env_content = config['configurations']['logfeeder-env']['content']
logfeeder_config_content = config['configurations']['logfeeder-input-configs']['content']
logfeeder_log4j_content = config['configurations']['logfeeder-log4j']['content']
logfeeder_pid_dir = config['configurations']['logfeeder-env']['logfeeder_pid_dir']
