#!/bin/bash

# Start up the VM
. ./common/start_vm.sh || { echo "Failed to start VM. Check your setup.config file."; return 1; }

### Set custom environment variables of the VM for code execution ###

# Check that the temporary environment variable file doesn't already exist from a prior failure
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="if [ -f /home/$VM_USERNAME/.temp-environment-vars ]; then rm /home/$VM_USERNAME/.temp-environment-vars; fi" \
|| { echo "ERROR: Failed to remove old temporary environment variable file"; return 1; }

# Create the new environment variable file
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="touch /home/$VM_USERNAME/.temp-environment-vars" \
|| { echo "ERROR: Failed to create a new environment variable file"; return 1; }

# Ensure the .temp-environment-vars file has permissions
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="chmod u+rwx /home/$VM_USERNAME/.temp-environment-vars" \
|| { echo "ERROR: Failed to change permissions of the .temp-environment-vars file"; return 1; }

# Write to the new environment variable file
echo "Please enter key/value pairs for your environment variables, one at a time."
echo "Example: MY_VARIABLE=my_value"
echo "Once you are finished all of your entries, enter 'done'"
USER_INPUT=""
while [ "$USER_INPUT" != "done" ]
do
  read -r USER_INPUT
  if [ "$USER_INPUT" != "done" ]
  then
    gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
    --command="echo \"\"$USER_INPUT\"\" >> /home/$VM_USERNAME/.temp-environment-vars" \
    || { echo "ERROR: Failed to add $USER_INPUT to .temp-environment-vars file"; return 1; }
  fi
done

# Confirm the environment variables entered
echo "Please confirm the following environment variables are correct by entering (yes/no):"
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="cat /home/$VM_USERNAME/.temp-environment-vars" \
|| { echo "ERROR: Failed to echo the environment variables set by the user"; return 1; }
read -r USER_INPUT
if [ "$USER_INPUT" == "yes" ]
then
  # Set the temporary file to the final file
  gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
  --command="mv /home/$VM_USERNAME/.temp-environment-vars /home/$VM_USERNAME/.environment-vars" \
  || { echo "ERROR: Failed to replace the .environment-vars file."; return 1; }
else
  echo "Exiting: submitted environment variables unconfirmed."
  # Delete the temporary file
  gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
  --command="rm /home/$VM_USERNAME/.temp-environment-vars" \
  || { echo "ERROR: Failed to delete the .temp-environment-vars file."; return 1; }
fi

# Shut down the VM
. ./common/stop_vm.sh || { echo "Failed to stop VM. Check your setup.config file."; return 1; }