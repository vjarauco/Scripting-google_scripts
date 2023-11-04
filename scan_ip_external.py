import subprocess
import os
from google.cloud import compute_v1
from google.auth import exceptions

PROJECT_INPUT = input("Enter project ID or leave it empty to list all projects: ")
if PROJECT_INPUT:
    with open("projects.txt", "w") as projects_file:
        projects_file.write(PROJECT_INPUT)
else:
    projects_cmd = "gcloud projects list --format='value(projectId)'"
    projects_list = subprocess.run(projects_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if projects_list.returncode == 0:
        with open("projects.txt", "w") as projects_file:
            projects_file.write(projects_list.stdout)
    else:
        print(projects_list.stderr)
        exit(1)

with open("projectsExternal_IPs.csv", "w") as output_file:
    output_file.write("Project\tInstance_Name\tExternal_Ip\tType\tMonthly_Cost\n")

def get_instance_monthly_cost(project_id, instance_name):
    try:
        client = compute_v1.InstancesClient()
        instance = client.get(project=project_id, zone="us-central1-a", instance=instance_name)
        machine_type = instance.machine_type.split("/")[-1]
        machine_types_client = compute_v1.MachineTypesClient()
        machine_type_info = machine_types_client.get(project=project_id, zone="us-central1-a", machineType=machine_type)
        hourly_rate = machine_type_info.guestCpus * machine_type_info.memoryMb / 1000.0
        monthly_rate = hourly_rate * 24 * 30
        return monthly_rate
    except exceptions.DefaultCredentialsError:
        print("Google Cloud SDK credentials not found. Please authenticate using 'gcloud auth login'.")
        return None

with open("projects.txt") as projects_file:
    for project_to_list_ips in projects_file:
        project_to_list_ips = project_to_list_ips.strip()
        compute_api_enabled_cmd = f"gcloud services list --project={project_to_list_ips}"
        compute_api_enabled = subprocess.run(compute_api_enabled_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if "compute.googleapis.com" in compute_api_enabled.stdout:
            print(f"Listing compute engine instances with external IP for project {project_to_list_ips} that has the Compute Engine API Enabled")
            compute_instances_cmd = f"gcloud compute instances list --flatten='networkInterfaces[].accessConfigs[]' --filter='networkInterfaces.accessConfigs.natIP:*' --format='value(project, name, networkInterfaces.accessConfigs.natIP, kind)' --project {project_to_list_ips}"
            compute_forwarding_rules_cmd = f"gcloud compute forwarding-rules list --format='value(project, name, IPAddress, kind)' --project {project_to_list_ips}"
            instances_list = subprocess.run(compute_instances_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            forwarding_rules_list = subprocess.run(compute_forwarding_rules_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if instances_list.returncode == 0 or forwarding_rules_list.returncode == 0:
                with open("projectsIPs.csv", "a") as output_file:
                    project_name_cmd = f"gcloud projects describe {project_to_list_ips} --format='value(name)'"
                    project_name_result = subprocess.run(project_name_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    project_name = project_name_result.stdout.strip() if project_name_result.returncode == 0 else ""
                    for line in instances_list.stdout.splitlines():
                        fields = line.split("\t")
                        project_id = fields[0]
                        instance_name = fields[1]
                        external_ip = fields[2]
                        kind = fields[3]
                        monthly_cost = get_instance_monthly_cost(project_id, instance_name)
                        if monthly_cost is not None:
                            output_file.write(f"{project_name}\t{instance_name}\t{external_ip}\t{kind}\t${monthly_cost:.2f}\n")
                    for line in forwarding_rules_list.stdout.splitlines():
                        fields = line.split("\t")
                        project_id = fields[0]
                        name = fields[1]
                        ip_address = fields[2]
                        kind = fields[3]
                        monthly_cost = 0  # Puedes personalizar esto en función de tus reglas de reenvío
                        output_file.write(f"{project_name}\t{name}\t{ip_address}\t{kind}\t${monthly_cost:.2f}\n")

if os.path.exists("temp.csv"):
    os.remove("temp.csv")
if os.path.exists("projects.txt"):
    os.remove("projects.txt")

print("\nFinished, please review the output in projectsExternal_IPs.csv")
