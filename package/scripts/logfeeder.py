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
    
    try: grp.getgrnam(params.logfeeder_group)
    except KeyError: Group(group_name=params.logfeeder_group) 
    
    try: pwd.getpwnam(params.logfeeder_user)
    except KeyError: User(username=params.logfeeder_user, 
                          gid=params.logfeeder_group, 
                          groups=[params.logfeeder_group], 
                          ignore_failures=True)    
          
    self.install_logfeeder()          
    Execute ('echo "logfeeder install complete"')


  def install_logfeeder(self):
    import params  
    import status_params

    Directory([params.logfeeder_log_dir, status_params.logfeeder_pid_dir, params.logfeeder_dir],
              mode=0755,
              cd_access='a',
              owner=params.logfeeder_user,
              group=params.logfeeder_group,
              recursive=True
          )


    File(params.logfeeder_log,
            mode=0644,
            owner=params.logfeeder_user,
            group=params.logfeeder_group,
            content=''
    )

    if params.logfeeder_downloadlocation == 'RPM':
      Execute('rpm -ivh http://TBD.rpm')
    else:  
      Execute('cd ' + params.logfeeder_dir + '; wget ' + params.logfeeder_downloadlocation + ' -O logfeeder.tar.gz -a ' + params.logfeeder_log, user=params.logfeeder_user)
      Execute('cd ' + params.logfeeder_dir + '; tar -xvf logfeeder.tar.gz', user=params.logfeeder_user)    

    
  def configure(self, env):
    import params
    import status_params

    env.set_params(params)

    #Duplicated here, because if the machine restarts /var/run folder is wiped out
    Directory([params.logfeeder_log_dir, status_params.logfeeder_pid_dir, params.logfeeder_dir],
              mode=0755,
              cd_access='a',
              owner=params.logfeeder_user,
              group=params.logfeeder_group,
              recursive=True
          )


    File(params.logfeeder_log,
            mode=0644,
            owner=params.logfeeder_user,
            group=params.logfeeder_group,
            content=''
    )

    
    #write content in jinja text field to logfeeder.properties
    env_content=InlineTemplate(params.logfeeder_env_content)
    File(format("{params.logfeeder_dir}/classes/logfeeder.properties"), content=env_content, owner=params.logfeeder_user)    

    #update the log4j
    file_content=InlineTemplate(params.logfeeder_log4j_content)    
    File(format("{params.logfeeder_dir}/classes/log4j.xml"), content=file_content, owner=params.logfeeder_user)    

    config_content=InlineTemplate(params.logfeeder_config_content)
    File(format("{params.logfeeder_dir}/classes/config.json"), content=config_content, owner=params.logfeeder_user)    
    

  #Call start.sh to start the service
  def start(self, env):

    #import properties defined in -config.xml file from params class
    import params

    #import status properties defined in -env.xml file from status_params class
    import status_params
    self.configure(env)

    #create pid/log dirs in case not there
    Directory([params.logfeeder_log_dir, status_params.logfeeder_pid_dir],
              mode=0755,
              cd_access='a',
              owner=params.logfeeder_user,
              group=params.logfeeder_group,
              recursive=True
          )
              
    Execute('find '+params.service_packagedir+' -iname "*.sh" | xargs chmod +x')
    cmd = params.service_packagedir + '/scripts/start_logfeeder.sh ' + params.logfeeder_dir + ' ' + params.logfeeder_log + ' ' + status_params.logfeeder_pid_file + ' ' + params.java64_home + ' ' + '-Xmx' + params.logfeeder_max_mem
  
    Execute('echo "Running cmd: ' + cmd + '"')    
    Execute(cmd, user=params.logfeeder_user)

  #Called to stop the service using the pidfile
  def stop(self, env):
    import params
     
    #import status properties defined in -env.xml file from status_params class  
    import status_params
    
    #this allows us to access the status_params.logfeeder_pid_file property as format('{logfeeder_pid_file}')
    env.set_params(status_params)

    if os.path.isfile(status_params.logfeeder_pid_file):
      Execute (format('kill `cat {logfeeder_pid_file}` >/dev/null 2>&1'), ignore_failures=True)

      #delete the pid file
      Execute (format("rm -f {logfeeder_pid_file}"), user=params.logfeeder_user)
      	
  #Called to get status of the service using the pidfile
  def status(self, env):
  
    #import status properties defined in -env.xml file from status_params class
    import status_params
    env.set_params(status_params)  
    
    #use built-in method to check status using pidfile
    check_process_status(status_params.logfeeder_pid_file)  

  def update_logfeeder(self, env):
    import params
    env.set_params(params)
    Execute('echo Stopping logfeeder')
    self.stop(env)
    Execute('echo Updating logfeeder using latest install bits')
    Execute(format("rm -rf {logfeeder_dir}/*"))
    self.install()
    Execute('echo Starting logfeeder')
    self.start(env)


if __name__ == "__main__":
  Master().execute()
