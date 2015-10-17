#!/usr/bin/env python
from resource_management import *

# config object that holds the status related configurations declared in the -env.xml file
config = Script.get_config()

# store the location of the stack service piddir from the 'stack_piddir' property of the 'solr-env.xml' file
logsearch_pid_dir = config['configurations']['logsearch-env']['logsearch_pid_dir']
logsearch_pid_file = format("{logsearch_pid_dir}/logsearch.pid")
