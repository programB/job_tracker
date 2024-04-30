SHELL := bash

IS_VENV_ACTIVE = $(shell [ $$PWD/venv/bin/python = $$(which python) ] && echo "YES" || echo "NO")

.PHONY: clean_source_tree local.venv.check local.initialize.environment local.reinitialize.environment local.update.constraints local.setup.environment local.run

local.venv.check:
	@if [ ${IS_VENV_ACTIVE} == "NO" ]; then \
		echo $$'STOP\n\nACTIVATE VIRTUAL ENVIRONMENT FIRST WITH: source ./venv/bin/activate' ;\
		false ;\
	fi

clean_source_tree: local.venv.check
	pyclean -v .

local.initialize.environment:
	@if [ -d "venv" ]; then \
		echo "Local environment already exists. To forcibly recreate it use: make local.reinitialize.environment" ;\
	else \
		echo "Creating virtual environment in 'venv' directory" ;\
		python -m venv venv --prompt front-end-sandbox ;\
	fi

local.reinitialize.environment:
	@if [ -d "venv" ]; then \
		echo "Removing existing virtual environment directory 'venv'" ;\
		rm -fr venv ;\
	fi
	@echo "Creating virtual environment in directory 'venv'"
	@python -m venv venv --prompt front-end-sandbox

local.update.constraints: local.venv.check
	@echo "Writing all dependencies to constraints.txt"
	@python -m pip freeze --exclude-editable > constraints.txt

local.setup.environment: local.venv.check
	@echo "Installing project in editable mode"
	@echo "Installing all project's dependencies at pinned versions"
	@python -m pip install --upgrade pip && python -m pip install -c constraints.txt --editable ".[dev]"

local.run: local.venv.check
	@echo "Running frontend app localy from source tree on port http://localhost:9022"
	@flask --app src/job_tracker_frontend run --host "0.0.0.0" --port "9022" --debug
