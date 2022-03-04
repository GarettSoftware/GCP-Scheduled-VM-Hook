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

### Change time of the cloud scheduler jobs ###

# Collect scheduler timezone
echo "Please see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for list of available timezones"
echo "Please enter the cloud scheduler time zone"
read -r SCHEDULER_TIMEZONE

# Collect VM timezone
echo "Please enter the VM timezone."
echo "Would you like to list the possible VM timezones? (y/n):"
read -r LIST_TIMEZONES
if [ "$LIST_TIMEZONES" == "y" ]
then
  # List the timezones available for the VM
  gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
  --command="timedatectl list-timezones" \
  || { echo "ERROR: Failed to list the available timezones for the VM"; return 1; }
fi
echo "Please enter the VM timezone:"
read -r VM_TIMEZONE

echo "Please see https://crontab.guru/ for cron formatting"
# Collect the cron times
echo "Please enter a VM start time (cron)"
read -r CHRON_START_INSTANCE
echo "Please enter a VM code run time (cron) (try 1-2 min after VM start up)"
read -r CHRON_START_HOOK
echo "Please enter a VM stop time (cron) (used for failsafe shutdown)"
read -r CHRON_STOP_INSTANCE

# Update the start job
gcloud scheduler jobs update pubsub start-instances \
--schedule "$CHRON_START_INSTANCE" \
--topic start-instance-event \
--message-body "{\"label\":\"$VM_LABEL_KEY=$VM_LABEL_VALUE\"}" \
--time-zone "$SCHEDULER_TIMEZONE" \
|| { echo "ERROR: Failed update start-instances PubSub"; return 1; }
# Update the stop job
gcloud scheduler jobs update pubsub stop-instances \
--schedule "$CHRON_STOP_INSTANCE" \
--topic stop-instance-event \
--message-body "{\"label\":\"$VM_LABEL_KEY=$VM_LABEL_VALUE\"}" \
--time-zone "$SCHEDULER_TIMEZONE" \
|| { echo "ERROR: Failed update stop-instances PubSub"; return 1; }


### Change time of VM crontab ###

# Set the timezone of the VM
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="sudo timedatectl set-timezone $VM_TIMEZONE" \
|| { echo "ERROR: Failed to set the VM timezone"; return 1; }

# Check that the temporary environment variable file doesn't already exist from a prior failure
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="if [ -f /home/$VM_USERNAME/crontab_file ]; then rm /home/$VM_USERNAME/crontab_file; fi" \
|| { echo "ERROR: Failed to remove old temporary crontab_file"; return 1; }

# Schedule the VM to run the bootstrap.sh after the VM wakes up
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="touch crontab_file" \
|| echo "WARNING: Failed to create a new, empty crontab file."

gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="echo \"\"SHELL=/bin/bash\"\" >> crontab_file" \
|| { echo "ERROR: Failed to add to crontab file"; return 1; }
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="echo \"\"\"$CHRON_START_HOOK\" /home/$VM_USERNAME/$REPOSITORY_NAME/hook/bootstrap.sh \>\> nightly-output.txt 2\>\&1\"\" >> crontab_file" \
|| { echo "ERROR: Failed to add to crontab file"; return 1; }
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="crontab crontab_file" \
|| { echo "ERROR: Failed to install crontab"; return 1; }
gcloud compute ssh "$VM_USERNAME"@"$COMPUTE_INSTANCE_NAME" --zone="$ZONE" \
--command="rm crontab_file" \
|| { echo "ERROR: Failed to clean up crontab_file"; return 1; }

# Shut down the VM
. ./common/stop_vm.sh || { echo "Failed to stop VM. Check your maintenance.config file."; return 1; }