#!/bin/bash

# Start up the VM
. ./common/start_vm.sh || { echo "Failed to start VM. Check your setup.config file."; return 1; }

# SSH into the VM
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE"

# Shut down the VM
. ./common/stop_vm.sh || { echo "Failed to stop VM. Check your setup.config file."; return 1; }
