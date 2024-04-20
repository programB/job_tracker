DC=docker compose

COMPOSE_FILE=job-tracker-compose.yaml
# Docker's progress option can be one of: auto, tty, plain, quiet
PROGRESS=plain

APP_PROFILE=prod
TEST_PROFILE=testing

.PHONY: help

help:
	@echo "To run the tests do: make tests"
	@echo "To monitor tests progress do: make tests.monitor"
	@echo ""
	@echo "To run full set of production containers do: make apps"
	@echo ""
	@echo "To stop and remove containers do: make down"
	@echo ""

sel_fla_back_end/requirements-dev.txt: sel_fla_back_end/pyproject.toml
	@python extract_deps.py sel_fla_back_end/pyproject.toml


.PHONY: apps.backend.remove-requirements-file apps apps.backend.logs apps.frontend.logs apps.frontend.show

apps.backend.remove-requirements-file:
	@rm -fr sel_fla_back_end/requirements-dev.txt

apps: sel_fla_back_end/requirements-dev.txt
	@$(DC) --progress ${PROGRESS} --file ${COMPOSE_FILE} --profile ${APP_PROFILE} up --build -d
	@$(DC) --file ${COMPOSE_FILE} ps
	make apps.frontend.show

apps.backend.logs:
	@$(DC) --file ${COMPOSE_FILE} --profile ${APP_PROFILE} logs -f job-tracker-backend

apps.frontend.logs:
	@$(DC) --file ${COMPOSE_FILE} --profile ${APP_PROFILE} logs -f job-tracker-frontend

apps.frontend.show:
	@echo "Connecting to front-end's web UI"
	@python -mwebbrowser http://127.0.0.1:9022

.PHONY: tests tests.backend.logs tests.backend.monitor test.monitor

tests: sel_fla_back_end/requirements-dev.txt
	@$(DC) --progress ${PROGRESS} --file ${COMPOSE_FILE} --profile ${TEST_PROFILE} up --build -d
	@$(DC) --file ${COMPOSE_FILE} ps

tests.backend.logs:
	@$(DC) --file ${COMPOSE_FILE} --profile ${TEST_PROFILE} logs -f job-tracker-backend-tests

tests.backend.monitor:
	@echo "Connecting to selenium monitoring web UI"
	@python -mwebbrowser http://127.0.0.1:4444
	@echo "Connecting to noVNC service provided by the selenium container"
	@echo "If the webpage asks for password enter: secret"
	@python -mwebbrowser http://127.0.0.1:7900

test.monitor:
	make tests.backend.monitor
	make tests.backend.logs


.PHONY: stop down

stop:
	@$(DC) --file ${COMPOSE_FILE} --profile ${APP_PROFILE} --profile ${TEST_PROFILE} stop

down:
	@$(DC) --file ${COMPOSE_FILE} --profile ${APP_PROFILE} --profile ${TEST_PROFILE} down
