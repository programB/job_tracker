import job_tracker

app = job_tracker.create_app()
app.run(host="localhost", port=9021)
