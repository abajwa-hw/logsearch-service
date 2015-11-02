#### An Ambari Stack for Logsearch
Ambari stack for easily installing and managing Logsearch on HDP cluster

- Download HDP 2.2 sandbox VM image (Sandbox_HDP_2.2_VMware.ova) from [Hortonworks website](http://hortonworks.com/products/hortonworks-sandbox/)
- Import Sandbox_HDP_2.2_VMware.ova into VMWare and set the VM memory size to 8GB
- Now start the VM
- After it boots up, find the IP address of the VM and add an entry into your machines hosts file e.g.
```
192.168.191.241 sandbox.hortonworks.com sandbox    
```
- Connect to the VM via SSH (password hadoop) and start Ambari server
```
ssh root@sandbox.hortonworks.com
/root/start_ambari.sh
```

- To deploy the Logsearch stack, run below
```
VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
git clone https://github.com/abajwa-hw/logsearch-service.git /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/LOGSEARCH
```

- Edit the `/var/lib/ambari-server/resources/stacks/HDP/$VERSION/role_command_order.json` file by adding the below entries to the middle of the file
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
- Then you can click on 'Add Service' from the 'Actions' dropdown menu in the bottom left of the Ambari dashboard:

On bottom left -> Actions -> Add service -> check Logsearch service -> Next -> Next -> Next -> Deploy

- Also ensure that the install location you are choosing (/opt/Logsearch by default) does not exist

- On successful deployment you will see the Logsearch service as part of Ambari stack and will be able to start/stop the service from here:
![Image](../master/screenshots/1.png?raw=true)

- You can see the parameters you configured under 'Configs' tab
![Image](../master/screenshots/2.png?raw=true)


#### Use Logsearch 

- Lauch the Logsearch webapp via navigating to http://sandbox.hortonworks.com:8888/

- Alternatively, you can launch it from Ambari via [iFrame view](https://github.com/abajwa-hw/iframe-view)
![Image](../master/screenshots/3.png?raw=true)



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

#### Automated deployment via blueprint

- Bring up 4 VMs imaged with RHEL/CentOS 6.x

- On non-ambari nodes, install ambari-agents and point them to ambari node
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


- Deploy cluster using blueprint
```
wget https://raw.githubusercontent.com/abajwa-hw/logsearch-service/master/blueprint-4node-logsearch.json

#if needed change the numshards, replicas based on your setup (default is 1 for each)
#vi blueprint-4node-logsearch.json

curl -u admin:admin -H  X-Requested-By:ambari http://localhost:8080/api/v1/blueprints/logsearchBP -d @blueprint-4node-logsearch.json

wget https://raw.githubusercontent.com/abajwa-hw/logsearch-service/master/cluster-4node.json
curl -u admin:admin -H  X-Requested-By:ambari http://localhost:8080/api/v1/clusters/logsearchCluster -d @cluster-4node.json
```


#### Remove Logsearch service

- To remove the Logsearch service: 
  - Delete the Solr collection
```
sudo -u solr /opt/lucidworks-hdpsearch/solr/bin/solr delete -c hadoop_logs
sudo -u solr /opt/lucidworks-hdpsearch/solr/bin/solr delete -c history
```  
  - Stop the service via Ambari
  - Delete the service
  
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
  - Remove artifacts 
  
    ```
rm -rf /opt/log*
rm -rf /etc/logsearch
rm -rf /var/log/log*
rm -rf /var/run/log*
    
rm -rf /var/lib/ambari-server/resources/stacks/HDP/2.3/services/LOGSEARCH
    ```
  - Restart Ambari
    ```
    service ambari restart
    ```