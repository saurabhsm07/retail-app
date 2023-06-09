docker_image_name = retail-app:0.0.1
target_loc = app
docker_run = docker run --rm --mount type=bind,source="$(shell pwd)/",target=/app/ $(docker_image_name)

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available targets:"
	@echo "build         Build docker image"
	@echo "test          Run tests"
	@echo "shell  	 Start Container and open an interactive shell"

.PHONY: build-docker-image
build-docker-image: ## Build the docker image and install python dependencies
	docker build --no-cache -t $(docker_image_name) .
	$(docker_run) pipenv install --dev


.PHONY: test
test:
	$(docker_run) pipenv run test

.PHONY: shell
shell:
	docker run --rm -it --mount type=bind,source="$(shell pwd)/",target=/$(target_loc)/ $(docker_image_name) /bin/bash

.PHONY: instal-python-module
