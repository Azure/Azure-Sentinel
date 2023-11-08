## Instructions for Quick Deployment
1. Get an Authomize Token from your tenant
     - ```authomizeToken``` - this is the Token generated in your Authomize tenant. Go to the configurations page, click API Tokens and select a Platform Token. Insert that token into the ```config.cfg``` file.
2. Get the Azure shared key and your customer id from Log analytics workspace
     - ```customer_id``` - this is the workspace id in your Logs analytics workspace [see image](./setupInfo/2023-03-29_18-45-33.png). Insert that token into the ```config.cfg``` file.
     - ```shared_key``` - this is the Logs analytics workspace. Go to the configurations page [see image](./setupInfo/2023-03-29_18-45-33.png). Insert that token into the ```config.cfg``` file.
3. DO NOT CHANGE:
    - ```authomizeURL = https://api.authomize.com/v2/incidents/search```
    - ```sentinelLog = Authomize_v2```
    - ```DateFileCFG = processdate.cfg```
4. Copy ```Azure-Sentinel\Solutions\Authomize\Data Connectors``` to a working directory ```<YourLocalWorkingDirectory>\Authomize\Data Connectors\```
5. Update the ```config.cfg``` file within the ```<YourLocalWorkingDirectory>\Authomize\Data Connectors\``` with the data you collected from points 1 and 2 above and save the file.
6. Create your your Ubuntu VM with Dokcer Engine
    
## Deploy an Ubuntu VM with Docker Engine
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fazure-quickstart-templates%2Fmaster%2Fapplication-workloads%2Fdocker%2Fdocker-simple-on-ubuntu%2Fazuredeploy.json" data-linktype="external"><img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg?sanitize=true" alt="Deploy To Azure" data-linktype="external"></a>

This template allows you to deploy an Ubuntu VM with Docker (using the Docker Extension) installed. You can run docker commands by connecting to the virtual machine with SSH. [More details can be found here.](https://learn.microsoft.com/en-us/samples/azure/azure-quickstart-templates/docker-simple-on-ubuntu/)

Following are the basic setup instructions to start the container:

7. Copy the ```<Data Connectors>``` directory to your Ubuntu VM with Docker Engine
8. Go to the ```<workingdirectory>\Data Connectors\``` directory you just copied to your Ubuntu VM with Docker Engine.
9. By default the scheduler will run every 2 hours looking for incidents. If you want to change that value then open the file authomizescheduler.py find the variable at the top of the file called ```NumberOfMinutes``` and change from ```120```. This default can be left as is unless you have a very busy environment. Do not go below ```30``` minutes.
    - ***NOTE:*** When the image starts it will initiate contact with your tenant and collect all currently open events. Once complete it will check for new events every 120 minutes.
10. Using the Docker file included build your docker image: [```docker build -t authomize:sentinel .```] .
11. Create a container and start it detached. This also mounts the volume authomize_apps which is needed to ensure we keep file states: [```docker run -d -v authomize_apps:/apps --name sentinel001 authomize:sentinel```] .
12. Check that the image is running with [```docker ps```] and look for sentinel001 with the image authomize:sentinel.
13. Run the following [```docker update --restart unless-stopped sentinel001```] to ensure the container changes the restart policy for an already running container. This will force your container to start if your host is ever restarted. [See docker content for more information](https://docs.docker.com/config/containers/start-containers-automatically/).

[DEV NOTE: consider using sparseCheckout]