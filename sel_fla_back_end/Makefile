.PHONY: docker_image, docker_image_from_scratch, get_global_requirements, remove_global_requirements, clean_source_tree, run_in_docker, run_chrome_in_docker, compose_up, compose_down, compose_app_shell

IMAGE_TAG=job-tracker-backend
CONTAINER_NAME=job-tracker-backend-service
COMPOSE_YAML_FILE = testrunner-docker-compose.yaml

docker_image:
	make get_global_requirements
	make clean_source_tree
	docker build --progress plain -t ${IMAGE_TAG} .
	make remove_global_requirements

docker_image_from_scratch: get_global_requirements
	make get_global_requirements
	make clean_source_tree
	docker build --progress plain --no-cache -t ${IMAGE_TAG} .
	make remove_global_requirements

get_global_requirements:
	cp ../pip-requirements.txt .

remove_global_requirements:
	rm -f pip-requirements.txt

clean_source_tree:
	pyclean -v .

run_in_docker:
	docker run -it --rm --name ${CONTAINER_NAME}-1 ${IMAGE_TAG}:latest sh

run_chrome_in_docker:
	docker run --rm -d --name standalone-chrome --ulimit nofile=65536:65536 -p 4444:4444 -p 7900:7900 -p 5900:5900 --shm-size="2g" selenium/standalone-chrome:4.17.0-20240123
	# When no longer needed stop the this container using:
	#   docker stop standalone-chrome
	# It will be automatically removed.

compose_up:
	docker compose --file ${COMPOSE_YAML_FILE} up -d

compose_down:
	docker compose --file ${COMPOSE_YAML_FILE} down

compose_app_shell:
	docker compose --file ${COMPOSE_YAML_FILE} exec job-tracker-backend sh
