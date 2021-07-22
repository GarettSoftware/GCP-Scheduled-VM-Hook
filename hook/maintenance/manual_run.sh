#!/bin/bash

# Load the config
. ./setup.config

# Set the active project for the gcloud CLI
gcloud config set project "$PROJECT_ID" \
&& echo "Project: $PROJECT_ID set" || { echo "ERROR: $PROJECT_ID incorrect in setup or permissions not granted."; return 1; }


### Manually startup the VM, run the application, download the logs, and shut down the VM ###

# Start up the VM
. ./common/start_vm.sh || { echo "Failed to start VM. Check your setup.config file."; return 1; }

# Run the bootstrap.sh file
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" --command=". /home/$VM_USERNAME/$REPOSITORY_NAME/hook/bootstrap.sh" 2> /dev/null

# Wait for VM to shut down (shut down triggered in run_hook.sh)
sleep 60

# Download the logs
. ./download_logs.sh