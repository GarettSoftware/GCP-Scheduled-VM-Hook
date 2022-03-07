#!/bin/bash

# MIT License

# Copyright (c) 2021 Garett MacGowan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Get the script directory (useful for moving files to and from VM)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Start up the VM
. ./common/start_vm.sh || { echo "Failed to start VM. Check your maintenance.config file."; return 1; }

### Download the logs from the VM ###

# Zip the logs folder
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="cd /home/$VM_USERNAME/$REPOSITORY_NAME/log/logs && zip -r /home/$VM_USERNAME/logs.zip ./" \
|| { echo "ERROR: Failed to zip the logs folder. May not exist... If issue persists, try SSH into VM to inspect."; return 1; }

# Download the zipped folder from the VM into the hook/logs directory
gcloud compute scp "$COMPUTE_INSTANCE_NAME":/home/"$VM_USERNAME"/logs.zip "$SCRIPT_DIR"/../../log/logs/vm_logs.zip --zone="$ZONE" \
|| { echo "ERROR: Failed to copy the logs.zip file off the VM"; return 1; }

# Delete the zipped folder on the VM
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="rm /home/$VM_USERNAME/logs.zip" \
|| { echo "ERROR: Failed to delete the logs.zip folder on the VM"; return 1; }

# Shut down the VM
. ./common/stop_vm.sh  || { echo "Failed to stop VM. Check your maintenance.config file."; return 1; }