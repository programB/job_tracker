import job_tracker

print("Starting server...")
app = job_tracker.create_app()
app.run(host="localhost", port=9021)
