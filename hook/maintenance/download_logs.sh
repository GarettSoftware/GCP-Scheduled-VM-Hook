#!/bin/bash

# Get the script directory (useful for moving files to and from VM)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Start up the VM
. ./common/start_vm.sh || { echo "Failed to start VM. Check your setup.config file."; return 1; }

### Download the logs from the VM ###

# Zip the logs folder
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="cd /home/$VM_USERNAME/$REPOSITORY_NAME/hook/logs && zip -r /home/$VM_USERNAME/logs.zip ./" \
|| { echo "ERROR: Failed to zip the logs folder. May not exist... If issue persists, try SSH into VM to inspect."; return 1; }

# Download the zipped folder from the VM into the hook/logs directory
gcloud compute scp "$COMPUTE_INSTANCE_NAME":/home/"$VM_USERNAME"/logs.zip "$SCRIPT_DIR"/../logs/vm_logs.zip --zone="$ZONE" \
|| { echo "ERROR: Failed to copy the logs.zip file off the VM"; return 1; }

# Delete the zipped folder on the VM
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="rm /home/$VM_USERNAME/logs.zip" \
|| { echo "ERROR: Failed to delete the logs.zip folder on the VM"; return 1; }

# Shut down the VM
. ./common/stop_vm.sh  || { echo "Failed to stop VM. Check your setup.config file."; return 1; }