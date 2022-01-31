# GCP-Scheduled-VM-Hook Usage Guide

## Prerequisites
To be fully functional, this repository assumes you have purchased Garett MacGowan's Scheduled Python Virtual Machine 
Template service. See https://garettmacgowan.com/services/scheduled_compute/ for details.

## What is this repository for?
This repository works in conjunction with the infrastructure set up by Garett in order to
execute the code for your use case on a virtual machine in Google Cloud, according to your
schedule.

The contents in the `hook` folder of this repository are necessary for the scheduled code
execution to work correctly.

`scheduler_hook.py` inside the `hook` folder can be:
1) Modified to execute code you have already written. (recommended)
2) Extended to execute code you have not written yet.

By default, `scheduler_hook.py` logs a `hello world` to the `log/logs' directory inside the virtual machine.

## Setup Instructions
See YouTube video here for walk-through: TODO

### Code Repository Setup
Let's set up where your application will live and receive updates.

#### Case 1: You Already Have Code
1) Copy the hook directory of this repository into your existing
repository.
2) Modify the `scheduler_hook.py` file to execute your existing code.
3) Ensure you have a requirements.txt file at the top level of your project (or copy the one here).
4) Ensure the /logs directory is present in your .gitignore (or copy the .gitignore here).

#### Case 2: No Code Yet
1) Hit the "Use this template" button at the top of this page to create a new repository using this template.
2) Take note of the name you gave the repository.

### Google Cloud Platform Account Setup
1) Set up a Google Cloud Platform (GCP) account
   https://cloud.google.com/
2) Set up a GCP project
   https://console.cloud.google.com/projectcreate
    - Keep track of the `Project ID`
3) Set up a billing account
   https://console.cloud.google.com/billing
4) Link the project to the billing account
   https://console.cloud.google.com/billing/projects
4) Ask Garett for the email address to add to the `Editor` role for the project (necessary for setup, you can revoke access after setup complete)
https://console.cloud.google.com/iam-admin/

### Prepare Answers to the Following Questions and Send to Garett
1) What is your `Project ID`? (created above)
2) What would you like the name of your VM instance to be? Use dashes `-` instead of spaces in the name.
3) What machine type do you want? If you don't know, ask Garett.
   https://cloud.google.com/compute/docs/machine-types
4) Do you need an accelerator? If you don't know, ask Garett.
    - For compute
      - `nvidia-tesla-t4`
      - `nvidia-tesla-v100`
      - `nvidia-tesla-p100`
      - `nvidia-tesla-p4`
      - `nvidia-tesla-k80`
    - For graphics
      - `nvidia-tesla-t4-vws`
      - `nvidia-tesla-p100-vws`
      - `nvidia-tesla-p4-vws`
    - Pricing https://cloud.google.com/compute/gpus-pricing
5) Do you have a zone preference (where the VM will be located)? https://cloud.google.com/compute/docs/regions-zones
    - Zone must be available for the requested hardware.
    - If you do not, a zone will be selected for you.
6) What boot disk size do you require?
7) Would you like to have an SSD boot device? If you don't know, probably not.
8) What would you like the VM username to be?
9) What python version do you want running your code?
   - e.g. `3.7.3`
10) What is the name of the git branch you want the VM to execute?
    - Default is `master`
11) What is the url of the repository you created above?
    - e.g., `git@github.com:GarettSoftware/GCP-Scheduled-VM-Hook.git` (SHOULD NOT BE THIS ONE)
12) What time zone would you like to be the basis for the schedule?
    - e.g., `UTC`
13) What time would you like the code to begin executing under the time zone?
14) How long do you expect the code to take to run to completion (one execution cycle)?
    - This is used to set up automatic VM shut down in the event of an unexpected failure.

### Cooperative Step
Here, you should wait for Garett to start the setup and send you an SSH key.

### Virtual Machine (VM) Repository Access
Since the repository run on the VM is yours (you have followed case 1 or case 2 above), you must add an SSH key to your
git hosting service. Once Garett sends you the key, you must add it to the profile associated with the repository host.
See here for the location on GitHub: https://github.com/settings/keys. You may name the key anything you like.

## Use Cases
### Anything Python
**If you have a repetitive, scheduled problem that has a software solution, you have a valid use case!**

Examples

- Scheduled Video Creation + Upload (See `https://www.youtube.com/c/ReddiTube` for example)
- Scheduled Machine Learning Training
- Scheduled Machine Learning Inference
- Scheduled Business Analytics Summaries / Alerts
  - Hook into your business APIs.
  - Write alert logic.
  - Use SMS messaging service to send alerts to relevant stakeholders.
- Scheduled Database Vacuum
- Scheduled Business Administration
  - Sending E-mail invoices to a network printer
- Scheduled Miscellaneous Batch Data Processing

If your use case isn't here, send me your use case, I will add it!

## Maintenance
In this repository, you will find a folder called `hook/maintainence` which contains various useful interactive scripts. 

### Changing the VM Run Times
The `time_change.sh` script takes you through the process of updating the execution timings
of the VM.

### Adding Environment Variables
In the event that your code utilizes environment variables, you may need a way to add them to the VM.
`manage_environment_vars.sh` provides an interface to add and remove environment variables used in the execution of 
your scripts.

### Downloading the Execution Logs
Sometimes, your code may not execute correctly on the VM due to configuration issues. In these cases, it is useful to
check the execution logs produced by the VM. `download_logs.sh` provides a way to download the logs from the VM.

### Running the Code Outside of Schedule
In the event that you need to manually trigger the VM code execution, `manual_run.sh` can help. This script may 
be invaluable in the event of a server outage during the scheduled run time.

### Recommendations
Try your best to keep your business logic safe from unexpected outages. GCP VMs are more resilient to
outages than local hardware, but there is always a small risk of failure (GCP scheduled outages).

### License Information
MIT License

Copyright (c) 2021 Garett MacGowan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.