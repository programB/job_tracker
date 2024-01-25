.PHONY: docker_image, docker_image_from_scratch, get_global_requirements, remove_global_requirements, clean_source_tree

IMAGE_TAG=job-tracker-backend

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
