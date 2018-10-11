#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing


cd /app/

export PYTHONPATH=/app/

# create database tables if not exists.
python kilogram/models.py

# slurp latest and greatest of kilogram.nl
python kilogram/slurp.py

# copy data into final table for serving to django
python kilogram/copy_to_model.py
