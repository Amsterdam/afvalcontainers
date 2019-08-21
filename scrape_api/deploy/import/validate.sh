#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

echo 'Check!' > log.txt
cat log.txt
curl -F file=@log.txt -F channels=niels-test  -H "Authorization: Bearer ${SLACK_ID}" https://slack.com/api/files.upload
