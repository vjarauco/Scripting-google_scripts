list-external-ips - A script to snapshot a list of VMs external IPs
Running the script
curl https://github.com/vjarauco/Scritping-google_scripts-.git) | bash
This execution will list all the project under the organizations the caller is authorized to list, and iterate through those projects searching for VMs that has an external IP assigned.

You can also execute this script for a single project by passing through the project name like below:

curl https://raw.githubusercontent.com/doitintl/list-external-ips/master/ext-ips-analysis.sh | bash -s nir-playground
Output
The script creates a file named projectsIPs.csv in the execution folder, like the one below:
