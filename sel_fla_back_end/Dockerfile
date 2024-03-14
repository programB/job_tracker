# -- def wheelbuilder --
# builds a wheel from the package upon successful
# completion of unit tests and static code analysis
#
# Docker community maintained image:
# - based on the slimmed down version of Debian 12 (aka 'bookworm', EOL in mid 2028)
# - with python 3.11.7 (last currently available version of the 3.11 series)
FROM python:3.11.7-slim-bookworm AS wheelbuilder

# Apply any security updates for Debian if they are available
RUN apt-get update && apt-get upgrade --yes

# Add non-privileged user to the system (inside container)
RUN useradd --create-home regularuser

# DROP ROOT PRIVILEGES by switching to regular user account
USER regularuser

# Set default directory for consecutive commands
WORKDIR /home/regularuser

# Set (permanently for current user) helper environment value
# pointing to the python's virtual environment (yet to be created)
ENV VIRTUALENV=/home/regularuser/venv

# Create python's virtual environment
RUN python3 -m venv $VIRTUALENV

# Modify user's PATH variable so that binaries inside the created
# virtual environment will take precedences over system wide installed ones
# (eg. python interpreter). This is equivalent to activating the environment.
# As every docker instructions spins up a new shell, activating the environment
# by sourcing the venv/bin/activate script wouldn't work - the environment
# would not have persisted.
ENV PATH="$VIRTUALENV/bin:$PATH"

# Copy over the project's definition and requirement's definition files
# to the image (changing file ownership).
# This is to keep docker layers as isolated as possible. Copying only
# necessary files explicitly and in separate steps
# avoids rebuilding entire image every time one of the
# project's files changes.
COPY --chown=regularuser pip-requirements.txt pyproject.toml .flake8 constraints.txt ./

# Install globally pinned pip version
# and upgrade setuptools to its latest version to avoid problems.
# Install (normal) dependencies at the versions pinned in the constraints.txt
# (do not create cache directory for the downloaded dependencies as
#  they won't be needed for anything else - reduces image size)
RUN python -m pip install --no-cache-dir -r pip-requirements.txt && \
  python -m pip install --no-cache-dir --upgrade setuptools && \
  python -m pip install --no-cache-dir -c constraints.txt ".[dev]"

# Copy over project's sources
COPY --chown=regularuser src/ src/
COPY --chown=regularuser test/ test/

# Install project's package
RUN python -m pip install . -c constraints.txt

# Run automated tests
# These should be self contained (unit tests!) because at this time
# no other services are available (unless they run on the web
# or on the host machine or a dedicated dockerized service is started and ready
# for these tests to use it).
# AND (if the tests pass) FINALLY build the wheel
RUN python -m pytest ./test/unit/ && \
  python -m flake8 src/ && \
  python -m isort src/ --check && \
  python -m black src/ --check --quiet && \
  python -m pylint src/ && \
  python -m bandit -r src/ --quiet && \
  python -m pip wheel --wheel-dir dist/ . -c constraints.txt
# -- end def wheelbuilder --

# -- def production image --
FROM python:3.11.7-slim-bookworm

RUN apt-get update && apt-get upgrade --yes

RUN useradd --create-home regularuser
USER regularuser
WORKDIR /home/regularuser

ENV VIRTUALENV=/home/regularuser/venv
RUN python3 -m venv $VIRTUALENV
ENV PATH="$VIRTUALENV/bin:$PATH"

# Copy over the wheel created by the wheelbuilder container to this image
COPY --from=wheelbuilder /home/regularuser/dist/job_tracker*.whl /home/regularuser

# Update tooling and install the wheel
RUN python -m pip install --upgrade pip setuptools && \
  python -m pip install --no-cache-dir job_tracker*.whl

# run whatever needs to be run
# CMD []
