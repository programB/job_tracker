#!/usr/bin/env bash

# start the app using development server
python -m flask --app src/job_tracker_frontend run --host 0.0.0.0 --port 9022 --debug
