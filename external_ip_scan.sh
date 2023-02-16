#!/bin/bash

PROJECT_INPUT=$1

if [[ $PROJECT_INPUT != "" ]]
then
	echo $PROJECT_INPUT > projects.txt
else
	gcloud projects list --format="value(projectId)" > projects.txt
	if [ "$?" -ne 0 ]
	then
		rm projects.txt
		exit 1
	fi
fi
echo "Project	Instance_Name	External_Ip	Type	Monthly_Cost" > projectsIPs.csv

while read project_to_list_ips; do
	COMPUTE_API_ENABLED=$(gcloud services list --project=$project_to_list_ips | grep compute.googleapis.com | wc -l)
	if [ "$COMPUTE_API_ENABLED" -eq "1" ] 
	then
		printf "Listing compute engine instances with external ip for project $project_to_list_ips that has the Compute Engine API Enabled\n"
		gcloud compute instances list --flatten="networkInterfaces[].accessConfigs[]" --filter="networkInterfaces.accessConfigs.natIP:*" --format="value(name, networkInterfaces.accessConfigs.natIP, kind)" --project $project_to_list_ips > temp.csv
		gcloud compute forwarding-rules list --format="value(name, IPAddress, kind)" --project $project_to_list_ips >> temp.csv	
		sed -i -e "s/^/$project_to_list_ips	/" temp.csv	
	fi
	if [ -f "./temp.csv" ]
	then
		cat temp.csv >> projectsIPs.csv		
	fi
done <projects.txt
if [ -f "./temp.csv" ]
then
	rm temp.csv projects.txt
else 
	rm projects.txt
fi


printf "\nFinished, Please review the output over projectsIPs.csv\n"
