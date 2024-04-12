.PHONY: docker_image, docker_image_from_scratch, remove_global_requirements, clean_source_tree, run_in_docker, run_locally

IMAGE_TAG=job-tracker-frontend

docker_image:
	make clean_source_tree
	docker build --progress plain -t ${IMAGE_TAG} .

docker_image_from_scratch:
	make clean_source_tree
	docker build --progress plain --no-cache -t ${IMAGE_TAG} .

clean_source_tree:
	rm -fr ./src/job_tracker_frontend/__pycache__/

run_in_docker:
	docker run --rm -p 9022:5000 --name web-frontend-1 ${IMAGE_TAG}:latest

run_locally:
	flask --app job_tracker_frontend run --host "0.0.0.0" --port "9022"
