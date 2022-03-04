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

# Start up the VM
. ./common/start_vm.sh || { echo "Failed to start VM. Check your maintenance.config file."; return 1; }

### Download file from VM ###

# Request file paths from user
LOCAL_FILE_PATH=""
VM_FILE_PATH=""

echo "Please enter the VM file path:"
read -r VM_FILE_PATH
echo "VM_FILE_PATH set to $VM_FILE_PATH"

echo "Please enter the local file path:"
read -r LOCAL_FILE_PATH
echo "LOCAL_FILE_PATH set to $LOCAL_FILE_PATH"

# Download the file from the VM to the local machine
gcloud compute scp "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME":"$VM_FILE_PATH" "$LOCAL_FILE_PATH" --zone="$ZONE" \
|| { echo "ERROR: Failed to copy the file off the VM"; return 1; }

# Shut down the VM
. ./common/stop_vm.sh  || { echo "Failed to stop VM. Check your maintenance.config file."; return 1; }