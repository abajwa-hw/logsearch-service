import sys, os, pwd, grp, signal, time, random
from resource_management import *
from subprocess import call

class Master(Script):

  #Call setup.sh to install the service
  def install(self, env):
  
    #import properties defined in -config.xml file from params class
    import params
    import status_params
      
    # Install packages listed in metainfo.xml
    self.install_packages(env)
    
    try: grp.getgrnam(params.logsearch_group)
    except KeyError: Group(group_name=params.logsearch_group) 
    
    try: pwd.getpwnam(params.logsearch_user)
    except KeyError: User(username=params.logsearch_user, 
                          gid=params.logsearch_group, 
                          groups=[params.logsearch_group], 
                          ignore_failures=True)    


    self.install_logsearch()    
  
    Execute ('echo "Logsearch install complete"')


  def install_logsearch(self):
    import params
    import status_params

    Directory([params.logsearch_log_dir, status_params.logsearch_pid_dir, params.logsearch_dir],
              mode=0755,
              cd_access='a',
              owner=params.logsearch_user,
              group=params.logsearch_group,
              recursive=True
          )


    File(params.logsearch_log,
            mode=0644,
            owner=params.logsearch_user,
            group=params.logsearch_group,
            content=''
    )

    if params.logsearch_downloadlocation == 'RPM':
      Execute('rpm -ivh http://s3.amazonaws.com/dev2.hortonworks.com/ashishujjain/logsearch/logsearch_2_3_2_0_2950-0.0.1.2.3.2.0-2950.el6.x86_64.rpm')
    else:
      Execute('cd ' + params.logsearch_dir + '; wget ' + params.logsearch_downloadlocation + ' -O logsearch-portal.tar.gz -a ' + params.logsearch_log, user=params.logsearch_user)
      Execute('cd ' + params.logsearch_dir + '; tar -xvf logsearch-portal.tar.gz', user=params.logsearch_user)


  def configure(self, env):
    import params
    import status_params

    env.set_params(params)

    #Duplicated in configure, because if the machine restart /var/run folder is deleted
    Directory([params.logsearch_log_dir, status_params.logsearch_pid_dir, params.logsearch_dir],
              mode=0755,
              cd_access='a',
              owner=params.logsearch_user,
              group=params.logsearch_group,
              recursive=True
          )


    File(params.logsearch_log,
            mode=0644,
            owner=params.logsearch_user,
            group=params.logsearch_group,
            content=''
    )

    #write content in jinja text field to system.properties
    env_content=InlineTemplate(params.logsearch_env_content)    
    File(format("{params.logsearch_dir}/classes/system.properties"), content=env_content, owner=params.logsearch_user)    

    #update the log4j
    file_content=InlineTemplate(params.logsearch_app_log4j_content)    
    File(format("{params.logsearch_dir}/classes/log4j.xml"), content=file_content, owner=params.logsearch_user)    

    #write content in jinja text field to solrconfig.xml for service logs
    file_content=InlineTemplate(params.logsearch_service_logs_solrconfig_content)    
    File(format("{params.logsearch_dir}/solr_configsets/hadoop_logs/conf/solrconfig.xml"), content=file_content, owner=params.logsearch_user)    

    #write content in jinja text field to solrconfig.xml for audit logs
    file_content=InlineTemplate(params.logsearch_audit_logs_solrconfig_content)    
    File(format("{params.logsearch_dir}/solr_configsets/audit_logs/conf/solrconfig.xml"), content=file_content, owner=params.logsearch_user)    

  #Call start.sh to start the service
  def start(self, env):

    #import properties defined in -config.xml file from params class
    import params

    #import status properties defined in -env.xml file from status_params class
    import status_params
    self.configure(env)

    env.set_params(params)
    Execute('echo metrics_collector_hosts ' + params.metrics_collector_hosts) 
    Execute('echo ambari_server_log_dir '+params.ambari_server_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo ambari_agent_log_dir '+params.ambari_agent_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo knox_log_dir '+params.knox_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo metrics_collector_log_dir '+params.metrics_collector_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo metrics_monitor_log_dir '+params.metrics_monitor_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo atlas_log_dir '+params.atlas_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo accumulo_log_dir '+params.accumulo_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo falcon_log_dir '+params.falcon_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo hbase_log_dir '+params.hbase_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo hdfs_log_dir_prefix '+params.hdfs_log_dir_prefix+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo hive_log_dir '+params.hive_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo kafka_log_dir '+params.kafka_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo oozie_log_dir '+params.oozie_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo ranger_usersync_log_dir '+params.ranger_usersync_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo ranger_admin_log_dir '+params.ranger_admin_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo ranger_kms_log_dir '+params.ranger_kms_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo storm_log_dir '+params.storm_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo yarn_log_dir_prefix '+params.yarn_log_dir_prefix+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo mapred_log_dir_prefix '+params.mapred_log_dir_prefix+' >> ' + params.logsearch_log, user=params.logsearch_user)
    Execute('echo zk_log_dir '+params.zk_log_dir+' >> ' + params.logsearch_log, user=params.logsearch_user)

    cmd = format('{logsearch_dir}/add_config_set.sh {solr_dir} {zookeeper_quorum}{solr_znode} hadoop_logs {logsearch_dir}/solr_configsets/hadoop_logs/conf')
    Execute(cmd)

    cmd = format('{logsearch_dir}/add_config_set.sh {solr_dir} {zookeeper_quorum}{solr_znode} audit_logs {logsearch_dir}/solr_configsets/audit_logs/conf')
    Execute(cmd)

    cmd = format('{logsearch_dir}/add_config_set.sh {solr_dir} {zookeeper_quorum}{solr_znode} history {logsearch_dir}/solr_configsets/history/conf')
    Execute(cmd)
    						 
    Execute('chmod -R ugo+r ' + params.logsearch_dir + '/solr_configsets')
    
    Execute('find '+params.service_packagedir+' -iname "*.sh" | xargs chmod +x')
    cmd = params.service_packagedir + '/scripts/start_logsearch.sh ' + params.logsearch_dir + ' ' + params.logsearch_log + ' ' + status_params.logsearch_pid_file + ' ' + params.java64_home + ' ' + '-Xmx' + params.logsearch_app_max_mem
  
    Execute('echo "Running cmd: ' + cmd + '"')    
    Execute(cmd, user=params.logsearch_user)

  #Called to stop the service using the pidfile
  def stop(self, env):
    import params
     
    #import status properties defined in -env.xml file from status_params class  
    import status_params
    
    #this allows us to access the status_params.logsearch_pid_file property as format('{logsearch_pid_file}')
    env.set_params(status_params)

    if os.path.isfile(status_params.logsearch_pid_file):
      Execute (format('kill `cat {logsearch_pid_file}` >/dev/null 2>&1'), ignore_failures=True)

      #delete the pid file. Let's not, so startup can check and kill -9 if needed
      #Execute (format("rm -f {logsearch_pid_file}"), user=params.logsearch_user)
      	
  #Called to get status of the service using the pidfile
  def status(self, env):
  
    #import status properties defined in -env.xml file from status_params class
    import status_params
    env.set_params(status_params)  
    
    #use built-in method to check status using pidfile
    check_process_status(status_params.logsearch_pid_file)  

  def update_logsearch(self, env):
    import params
    env.set_params(params)
    Execute('echo Stopping logsearch')
    self.stop(env)
    Execute('echo Updating logsearch using latest install bits')
    Execute(format("rm -rf {logsearch_dir}/*"))
    self.install_logsearch()
    Execute('echo Starting logsearch')
    self.start(env)

if __name__ == "__main__":
  Master().execute()
