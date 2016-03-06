#### An Ambari Stack for Logsearch
Ambari stack for easily installing and managing Logsearch on HDP cluster

Limitations:

- This is not an officially supported service and *is not meant to be deployed in production systems*. It is only meant for testing demo/purposes
- It does not support Ambari/HDP upgrade process and will cause upgrade problems if not removed prior to upgrade
- current version expects Logsearch component to be located on one of the nodes where Solr Cloud is installed.


There are two options to deploy Logsearch from Ambari:
  - Option 1: Deploy Logsearch on existing cluster
  - Option 2: Automated deployment of fresh cluster via blueprint

#### Option 1: Deploy Logsearch on existing cluster

The below steps demonstrate how to deploy Logsearch on existing cluster using the sandbox as an example. The same process can be followed on an Ambari installed cluster.

- Download HDP 2.2 sandbox VM image (Sandbox_HDP_2.2_VMware.ova) from [Hortonworks website](http://hortonworks.com/products/hortonworks-sandbox/)
- Import Sandbox_HDP_2.2_VMware.ova into VMWare and set the VM memory size to 8GB
- Now start the VM
- After it boots up, find the IP address of the VM and add an entry into your machines hosts file e.g.
```
192.168.191.241 sandbox.hortonworks.com sandbox    
```
- Connect to the VM via SSH (password hadoop) 
```
ssh root@sandbox.hortonworks.com
```

- To deploy the Logsearch stack, run below
```
VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
sudo git clone https://github.com/abajwa-hw/logsearch-service.git /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/LOGSEARCH
```

- Edit the role_command_order.json file ...
```
sudo vi /var/lib/ambari-server/resources/stacks/HDP/$VERSION/role_command_order.json
```
...by adding the below entries to the middle of the file
```
    "LOGSEARCH_SOLR-START" : ["ZOOKEEPER_SERVER-START"],
    "LOGSEARCH_MASTER-START": ["LOGSEARCH_SOLR-START"],
    "LOGSEARCH_LOGFEEDER-START": ["LOGSEARCH_SOLR-START", "LOGSEARCH_MASTER-START"],
```

- Restart Ambari
```
#on sandbox
sudo service ambari restart

#on non-sandbox
sudo service ambari-server restart

```
- Then you can click on 'Add Service' from the 'Actions' dropdown menu in the bottom left of the Ambari dashboard. 
- **Note that if running on multinode cluster**:
  - on the screen where you place the services, you can use press the + button next to Solr to install it on multiple nodes
  - The current version of the service expects Logsearch component to be located on one of the nodes where Solr Cloud is installed.
  
On bottom left -> Actions -> Add service -> check Logsearch service -> Next -> Next -> Next -> Deploy


- Also ensure that the install location you are choosing (/opt/logsearch by default) does not exist

- Now follow the steps [below](https://github.com/abajwa-hw/logsearch-service#use-logsearch) to start using Logsearch




#### Option 2: Automated deployment of fresh cluster via blueprint

- Bring up 4 VMs imaged with RHEL/CentOS 6.x (e.g. node1-4 in this case)

- On non-ambari nodes, install ambari-agents and point them to ambari node (e.g. node1 in this case)
```
export ambari_server=node1
curl -sSL https://raw.githubusercontent.com/seanorama/ambari-bootstrap/master/ambari-bootstrap.sh | sudo -E sh
```

- On Ambari node, install ambari-server
```
export install_ambari_server=true
curl -sSL https://raw.githubusercontent.com/seanorama/ambari-bootstrap/master/ambari-bootstrap.sh | sudo -E sh
yum install -y git
git clone https://github.com/abajwa-hw/logsearch-service.git /var/lib/ambari-server/resources/stacks/HDP/2.3/services/LOGSEARCH
```


- Edit the `/var/lib/ambari-server/resources/stacks/HDP/2.3/role_command_order.json` file to include below:
```
    "LOGSEARCH_SOLR-START" : ["ZOOKEEPER_SERVER-START"],
    "LOGSEARCH_MASTER-START": ["LOGSEARCH_SOLR-START"],
    "LOGSEARCH_LOGFEEDER-START": ["LOGSEARCH_SOLR-START", "LOGSEARCH_MASTER-START"],
```    

- Restart Ambari
```
service ambari-server restart
service ambari-agent restart    
```

- Confirm 4 agents were registered and agent remained up
```
curl -u admin:admin -H  X-Requested-By:ambari http://localhost:8080/api/v1/hosts
service ambari-agent status
```

- (Optional) - In general you can generate BP and cluster file using Ambari recommendations API using these steps. However in this example we are providing some sample blueprints which you can edit, so this is not needed
For more details, on the bootstrap scripts see bootstrap script git

```
yum install -y python-argparse
git clone https://github.com/seanorama/ambari-bootstrap.git

#optional - limit the services for faster deployment

#for minimal services
export ambari_services="HDFS MAPREDUCE2 YARN ZOOKEEPER HIVE LOGSEARCH"

#for most services
#export ambari_services="ACCUMULO FALCON FLUME HBASE HDFS HIVE KAFKA KNOX MAHOUT OOZIE PIG SLIDER SPARK SQOOP MAPREDUCE2 STORM TEZ YARN ZOOKEEPER LOGSEARCH"

export deploy=false
cd ambari-bootstrap/deploy
bash ./deploy-recommended-cluster.bash

cd tmpdir*

#edit the blueprint to customize as needed. You can use sample blueprints provided below to see how to add the custom services.
vi blueprint.json

#edit cluster file if needed
vi cluster.json
```


- Download either minimal or full blueprint
```
#Pick one of the below blueprints
#for minimal services download this one
wget https://raw.githubusercontent.com/abajwa-hw/logsearch-service/master/blueprint-4node-logsearch-minimal.json -O blueprint-4node-logsearch.json

#for most services download this one
wget https://raw.githubusercontent.com/abajwa-hw/logsearch-service/master/blueprint-4node-logsearch-all.json -O blueprint-4node-logsearch.json

#if needed change the numshards, replicas based on your setup (default is 2 for each)
#vi blueprint-4node-logsearch.json
```

- Upload selected blueprint and deploy cluster called logsearchCluster
```
curl -u admin:admin -H  X-Requested-By:ambari http://localhost:8080/api/v1/blueprints/logsearchBP -d @blueprint-4node-logsearch.json

wget https://raw.githubusercontent.com/abajwa-hw/logsearch-service/master/cluster-4node.json
curl -u admin:admin -H  X-Requested-By:ambari http://localhost:8080/api/v1/clusters/logsearchCluster -d @cluster-4node.json
```
- You can monitor the progress of the deployment via Ambari (e.g. http://node1:8080). 


#### Use Logsearch 

- On successful deployment you will see the Logsearch service as part of Ambari stack and will be able to start/stop the service from here:
![Image](../master/screenshots/ambari-logsearch.png?raw=true)

- You can see the parameters you configured under 'Configs' tab
![Image](../master/screenshots/ambari-logsearch-config.png?raw=true)

- The SolrCloud console should be available at http://sandbox.hortonworks.com:8886. Check that the hadoop_logs and history collections got created
![Image](../master/screenshots/logsearch-solr.png?raw=true)

- Launch the Logsearch webapp via navigating to http://sandbox.hortonworks.com:8888/
![Image](../master/screenshots/logsearch-dashboard.png?raw=true)

- Alternatively, you can launch it from Ambari via [iFrame view](https://github.com/abajwa-hw/iframe-view)
![Image](../master/screenshots/3.png?raw=true)


- After a few seconds you will see the HDP components indexed by Logsearch appear under each node. Hovering over each component will provide a summary of the types of errors (fatal, error, info etc) and the ability to drill into those messages.
![Image](../master/screenshots/logsearch-components.png?raw=true)

- You can use the Logsearch webapp user experience to explore cluster logs:
  - visualize histogram of log events based on level (fatal, error etc)
  - drill into logs based on:
    - log level
    - custom time range
    - node
    - component
    - etc
  - filter out (or in) messages based on keywords by selecting log text
  - view logs in tabular or file format
  - ability to add your own logs by modifiying the json document under Ambari > Log Search > Configs > Advanced logfeeder env > logfeeder-env template
    - first add the location of the log under 
    ```
    	{
			"type":"myservice",
			"rowtype":"service",
			"path":"/var/log/myservice/myservice_*.log"
		},
    ```
    - then add a grok entry for your service and include log4j format and message pattern 
    ```
    	{
			"filter":"grok",
			"conditions":{
				"fields":{
					"type":[
						"myservice"
					]
				}
			},
			"log4j_format":"%d{DATE} %5p [%t] %c{1}:%L - %m%n",
			"multiline_pattern":"^(%{USER_SYNC_DATE:logtime})",
			"message_pattern":"(?m)^%{USER_SYNC_DATE:logtime}%{SPACE}%{LOGLEVEL:level}%{SPACE}\\[%{DATA:thread_name}\\]%{SPACE}%{JAVACLASS:logger_name}:%{INT:line_number}%{SPACE}-%{SPACE}%{GREEDYDATA:log_message}",
			"post_map_values":{
				"logtime":{
					"map_date":{
						"date_pattern":"dd MMM yyyy HH:mm:ss"
					}
				}
			}
		},
    ```


#### Remote management 

- One benefit to wrapping the component in Ambari service is that you can now monitor/manage this service remotely via REST API
```
export SERVICE=LOGSEARCH
export PASSWORD=admin
export AMBARI_HOST=localhost

#detect name of cluster
output=`curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari'  http://$AMBARI_HOST:8080/api/v1/clusters`
CLUSTER=`echo $output | sed -n 's/.*"cluster_name" : "\([^\"]*\)".*/\1/p'`


#get service status
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X GET http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#start service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Start $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#stop service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Stop $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE
```

#### Remove Logsearch service

- To remove the Logsearch service: 
  - Login as solr
```
su - solr
```  
  - Delete the Solr collection
```
export SOLR_INCLUDE=/etc/logsearch/solr/solr.in.sh
/opt/lucidworks-hdpsearch/solr/bin/solr delete -c hadoop_logs
/opt/lucidworks-hdpsearch/solr/bin/solr delete -c history
```  
  - Stop the service via Ambari
  - Delete Logsearch Zookeeper dir
```
export JAVA_HOME=<JAVA_HOME used by Ambari>
/opt/lucidworks-hdpsearch/solr/server/scripts/cloud-scripts/zkcli.sh -zkhost localhost:2181 -cmd clear /logsearch  
```  
  - Delete the service from Ambari node
  
```
export SERVICE=LOGSEARCH
export PASSWORD=admin
export AMBARI_HOST=localhost

#detect name of cluster
output=`curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari'  http://$AMBARI_HOST:8080/api/v1/clusters`
CLUSTER=`echo $output | sed -n 's/.*"cluster_name" : "\([^\"]*\)".*/\1/p'`
   
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X DELETE http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#if above errors out, run below first to fully stop the service
#curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Stop $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

```
  - Remove artifacts from all nodes

```
rm -rf /opt/log*
rm -rf /etc/log*
rm -rf /var/log/log*
rm -rf /var/run/log*
```
  - (Optional) Remove Logsearch Ambari service from Ambari node
```  
rm -rf /var/lib/ambari-server/resources/stacks/HDP/2.3/services/LOGSEARCH
```
  - Restart Ambari
```
#sandbox
service ambari restart
    
#nonsandbox
service ambari-server restart
```