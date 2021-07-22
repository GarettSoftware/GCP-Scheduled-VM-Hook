#!/bin/bash

# Load the config
. ./setup.config

# Set the active project for the gcloud CLI
gcloud config set project "$PROJECT_ID" \
&& echo "Project: $PROJECT_ID set" || { echo "ERROR: $PROJECT_ID incorrect in setup or permissions not granted."; return 1; }

# Check if VM already running
if gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" --command="echo \"checking VM state...\"" 2> /dev/null
then
  echo "VM already running!"
else
  # Start up the VM
  gcloud scheduler jobs run start-instances \
  || { echo "ERROR: Failed to run start-instances (test)"; return 1; }
  # Ensure VM is awake
  echo "Please wait 60 seconds for the VM to start up"
  sleep 60
  if gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" --command="echo \"checking VM state...\"" 2> /dev/null
  then
    echo "VM successfully started"
  else
    { echo "VM not successfully started"; return 1; }
  fi
fi