docker_image_name = retail-app:0.0.1
target_loc = app
docker_run = docker run --rm --mount type=bind,source="$(shell pwd)/",target=/app/ $(docker_image_name)

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available targets:"
	@echo "build-docker-image		Build docker image"
	@echo "run-tests			Run tests"
	@echo "lint				Find linting errors"
	@echo "tidy				Tidy up your code"
	@echo "start-shell			Start Container and open an interactive shell"


.PHONY: build-docker-image
build-docker-image: ## Build the docker image and install python dependencies
	docker build --no-cache --build-arg  ENVIRONMENT=dev -t $(docker_image_name) . > ./local/docker/build.log 2>&1


.PHONY: run-tests
run-tests:
	$(docker_run) pipenv run test


.PHONY: lint
lint:
	$(docker_run) pipenv run lint

.PHONY: tidy
tidy:
	$(docker_run) pipenv run tidy


.PHONY: start-shell
start-shell:
	docker run --rm -it --mount type=bind,source="$(shell pwd)/",target=/$(target_loc)/ $(docker_image_name) /bin/bash
