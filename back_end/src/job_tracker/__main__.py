# pylint: skip-file
# This file is only needed if one wants to start the app
# by "running the module" (eg.: 'python -m job_tracker')
# Note that address and port are fixed and also
# create_app() instantiates the app object with its
# default configuration.

import job_tracker

print("Starting server...")
app = job_tracker.create_app()
app.run(host="0.0.0.0", port=5000)  # nosec B104
