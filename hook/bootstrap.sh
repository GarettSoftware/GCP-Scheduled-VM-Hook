#!/bin/bash

. ~/.profile
. ~/.environment-vars
. ~/."$VM_USERNAME"-bashrc

if [ ! -z "$GIT_BRANCH_NAME" ]
then
    git checkout "$GIT_BRANCH_NAME"
fi
git pull

pip install -r requirements.txt

. hook/run_hook.sh
