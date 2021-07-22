#!/bin/bash

# Load the config
. ./setup.config

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