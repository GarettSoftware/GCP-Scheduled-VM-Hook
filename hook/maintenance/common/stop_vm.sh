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

# Load the config
. ./maintenance.config

# Set the active project for the gcloud CLI
gcloud config set project "$PROJECT_ID" \
&& echo "Project: $PROJECT_ID set" || { echo "ERROR: $PROJECT_ID incorrect in setup or permissions not granted."; return 1; }

# Check if VM already shut down.
if ! gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" --command="echo \"checking VM state...\"" 2> /dev/null
then
  echo "VM already shut down!"
else
  # Shut down the VM
  gcloud scheduler jobs run stop-instances \
  || { echo "ERROR: Failed to run stop-instances"; return 1; }
  # Ensure VM is shut down
  echo "Please wait 60 seconds for the VM to shut down"
  sleep 60
  if ! gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" --command="echo \"checking VM state...\"" 2> /dev/null
  then
    echo "VM successfully shut down"
  else
    { echo "VM not successfully shut down"; return 1; }
  fi
fi