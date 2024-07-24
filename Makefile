app_web_image_name = retail-app:0.0.1
app_db_image_name = retail-db:0.0.1
target_loc = app

local_network_name = retail_app_nw
postgres_container_name = postgres_db
docker_run_cmd = docker run --rm --network $(local_network_name) --mount type=bind,source="$(shell pwd)/",target=/app/


.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available targets:"
	@echo "build-docker-images		Build docker images"
	@echo "run-tests			Run tests.\n\t\t\t\tOptional variable ENV=dev/local to run against dev env (postgres container) or local system (sql-lite)."
	@echo "lint				Find linting errors"
	@echo "tidy				Tidy up your code"
	@echo "start-shell			Start Container and open an interactive shell"


.PHONY: build-docker-image
build-docker-images: ## Build the docker images (DB and web app)
	docker build --no-cache --build-arg  ENVIRONMENT=dev -t $(app_db_image_name) -f Dockerfile.db . > ./local/docker/build_db.log 2>&1
	docker build --no-cache --build-arg  ENVIRONMENT=dev -t $(app_web_image_name) -f Dockerfile.web . > ./local/docker/build_web.log 2>&1


.PHONY: run-tests
run-tests:
ifeq ($(or $(strip $(ENV)),local),local)
	@echo "running tests in LOCAL Environment."
	docker network create $(local_network_name)
	$(docker_run_cmd) -e ENV=LOCAL $(app_web_image_name) pipenv run test
	docker network rm $(local_network_name)
else ifeq ($(strip $(ENV)),dev)
	@echo "running tests for DEV Environment."
	docker network create $(local_network_name)
	docker run -d -p 5432:5432 --network $(local_network_name) --mount type=bind,source=./scripts/db/,target=/docker-entrypoint-initdb.d/ --name $(postgres_container_name) $(app_db_image_name)
	$(docker_run_cmd) -e ENV=$(ENV) $(app_web_image_name) pipenv run test
	docker stop $(postgres_container_name)
	docker container rm -f $(postgres_container_name)
	docker network rm $(local_network_name)
else
	@echo "ERROR ! we can only run unit tests suite in LOCAL or DEV environments"
endif

.PHONY: lint
lint:
	$(docker_run_cmd) $(app_web_image_name) pipenv run lint

.PHONY: tidy
tidy:
	$(docker_run_cmd) $(app_web_image_name) pipenv run tidy


.PHONY: start-shell-web
start-shell-web:
	docker run --rm -it --mount type=bind,source="$(shell pwd)/",target=/$(target_loc)/ $(app_web_image_name) /bin/bash
