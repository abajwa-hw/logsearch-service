import sys, os, pwd, grp, signal, time
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
  
   
    Execute ('echo "Logsearch install complete"')



  def configure(self, env):
    import params
    env.set_params(params)
    
    #write content in jinja text field to system.properties
    env_content=InlineTemplate(params.logsearch_env_content)
    File(format("{params.logsearch_dir}/classes/system.properties"), content=env_content, owner=params.logsearch_user)    
    

  #Call start.sh to start the service
  def start(self, env):

    #import properties defined in -config.xml file from params class
    import params

    #import status properties defined in -env.xml file from status_params class
    import status_params
    self.configure(env)
    
    #create prerequisite Solr collections, if not already exist
    cmd = params.solr_bindir+'/solr create -c hadoop_logs -d '+params.logsearch_dir+'/solr_configsets/hadoop_logs/conf -s '+params.logsearch_numshards+' -rf ' + params.logsearch_repfactor
    Execute('echo '  + cmd)
    Execute(cmd, ignore_failures=True)

    cmd = params.solr_bindir+'/solr create -c history -d '+params.logsearch_dir+'/solr_configsets/history/conf -s '+params.logsearch_numshards+' -rf ' + params.logsearch_repfactor
    Execute('echo '  + cmd)
    Execute(cmd, ignore_failures=True)
    						 
    Execute('chmod -R ugo+r ' + params.logsearch_dir + '/solr_configsets')
    
    Execute('find '+params.service_packagedir+' -iname "*.sh" | xargs chmod +x')
    cmd = params.service_packagedir + '/scripts/start_logsearch.sh ' + params.logsearch_dir + ' ' + params.logsearch_log + ' ' + status_params.logsearch_pid_file + ' ' + params.java64_home
  
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

      #delete the pid file
      Execute (format("rm -f {logsearch_pid_file}"), user=params.logsearch_user)
      	
  #Called to get status of the service using the pidfile
  def status(self, env):
  
    #import status properties defined in -env.xml file from status_params class
    import status_params
    env.set_params(status_params)  
    
    #use built-in method to check status using pidfile
    check_process_status(status_params.logsearch_pid_file)  



if __name__ == "__main__":
  Master().execute()
