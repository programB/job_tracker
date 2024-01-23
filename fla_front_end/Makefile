.PHONY: docker_image, docker_image_from_scratch, get_global_requirements, remove_global_requirements

IMAGE_TAG=job-tracker-backend

docker_image:
	make get_global_requirements
	docker build -t ${IMAGE_TAG} .
	make remove_global_requirements

docker_image_from_scratch: get_global_requirements
	make get_global_requirements
	docker build --no-cache -t ${IMAGE_TAG} .
	make remove_global_requirements

get_global_requirements:
	cp ../pip-requirements.txt .

remove_global_requirements:
	rm -f pip-requirements.txt
