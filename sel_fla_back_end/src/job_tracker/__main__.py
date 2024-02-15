import job_tracker.app

app = job_tracker.app.create_app()
app.run(host="localhost", port=9021)
