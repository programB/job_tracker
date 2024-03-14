import job_tracker

print("Starting server...")
app = job_tracker.create_app()
app.run(host="0.0.0.0", port=5000)  # nosec B104
