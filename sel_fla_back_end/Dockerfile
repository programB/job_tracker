# -- def wheelbuilder --
# builds a wheel from the package
# can be used to run unit tests and static code analysis
#
# Docker community maintained image:
# - based on the slimmed down version of Debian 12 (aka 'bookworm', EOL in mid 2028)
# - with python 3.11.7 (last currently available version of the 3.11 series)
FROM python:3.11.7-slim-bookworm AS wheelbuilder

# Install Debian's updates if any
RUN apt-get update && apt-get upgrade --yes

# Add non-privileged user
RUN useradd --create-home regularuser

# DROP ROOT PRIVILEGES by switching to regular user account
USER regularuser

# Set default directory for consecutive commands
WORKDIR /home/regularuser

# Set environment variable pointing to
# the python's virtual environment
ENV VIRTUALENV=/home/regularuser/venv

# Create python's virtual environment
RUN python3 -m venv $VIRTUALENV

# Modify user's PATH variable so that binaries inside the virtual environment
# directory will take precedences over system wide installed ones
# (eg. python interpreter).
# As every docker instructions spins up a new shell, activating the environment
# by sourcing the venv/bin/activate script wouldn't work - the environment
# would not have persisted.
ENV PATH="$VIRTUALENV/bin:$PATH"

# Copy over the project's definition and requirements
# (changing file ownership), but not project sources.
# This is to keep docker layers isolated - a change in source files, not
# involving adding/removing dependencies, will not trigger a rebuild of this layer.
COPY --chown=regularuser pyproject.toml .flake8 constraints.txt ./

# a) Install latest pip (from PyPi)
# b) Download (or download and build) wheels for project's (in this directory - first dot)
#    obligatory dependencies (the "."). But don't install anything.
# c) Download the wheels for the setuptools, pip and wheel packages themselves
#    store downloaded/built wheels in wheels_made_by_pip directory for later
#    reuse in the second stage docker image
RUN python -m pip install --upgrade pip && \
  python -m pip wheel --wheel-dir wheels_made_by_pip . -c constraints.txt "." && \
  python -m pip wheel --wheel-dir wheels_made_by_pip setuptools pip wheel

# Install collected wheels (do not re-download them from PyPi)
RUN python -m pip install --no-index --find-links=wheels_made_by_pip/ --upgrade wheels_made_by_pip/*.whl

# Copy over project's sources
COPY --chown=regularuser src/ src/

# Optionally:
# Install project's development dependencies
# Don't create any cache for whatever needs to be downloaded - these packages
# are needed only in this 1st stage image (wheelbuilder).
# Since pip does not support selective install of optional dependencies
# eg. this will not work: python -m pip install --no-cache-dir -c constraints.txt "[dev]"
# use development dependencies list created by a helper script
# COPY --chown=regularuser requirements-dev.txt ./
# RUN python -m pip install --no-cache-dir -r requirements-dev.txt -c constraints.txt
# Copy over testing code
# COPY --chown=regularuser test/ test/

# Install project's package
# (do not (re)install dependencies,
#  all dependencies were already installed in previous steps)
RUN python -m pip install --no-deps .

# Optionally:
# Run tests
# RUN python -m pytest ./test/unit/ && \
#   echo "Running static code analysis" && \
#   python -m flake8 src/ && \
#   python -m isort src/ --check && \
#   python -m black src/ --check --quiet && \
#   python -m pylint src/ && \
#   python -m bandit -r src/ --quiet

# AND FINALLY build the wheel for our package
RUN python -m pip wheel --wheel-dir wheels_made_by_pip/ . -c constraints.txt
# -- end def wheelbuilder --

# -- def final_image --
# Installs wheels from the wheelbuilder step without re-downloading dependencies
# To reduce final image size this step is not copying any testing code
# or installing development dependencies
#
FROM python:3.11.7-slim-bookworm as final_image

# Install Debian's updates if any
# and remove the leftovers in one step to reduce layer's size
RUN apt-get update && apt-get upgrade --yes && \
  apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN useradd --create-home regularuser
USER regularuser
WORKDIR /home/regularuser

ENV VIRTUALENV=/home/regularuser/venv
RUN python3 -m venv $VIRTUALENV
ENV PATH="$VIRTUALENV/bin:$PATH"

# Copy the wheel of the created package and the wheels of the obligatory dependencies
# from the wheelbuilder step
COPY --from=wheelbuilder --chown=regularuser /home/regularuser/wheels_made_by_pip/ /home/regularuser/wheels
# Copy over pyproject.toml
COPY --from=wheelbuilder --chown=regularuser /home/regularuser/pyproject.toml /home/regularuser/pyproject.toml

# a) Install saved pip and setuptools first
# b) Install the wheel of created package and re-use saved wheels of its dependencies
RUN python -m pip install --no-cache-dir --no-index --find-links=wheels/ --upgrade pip setuptools && \
  python -m pip install --no-cache-dir --no-index --find-links=wheels/ wheels/job_tracker*.whl

# If this image is to be run standalone (as opposed to overriding the 'CMD'
# through to 'command' statement in docker compose yaml)
# run the installed package using the uvicorn ASGI server.
# Note: The app will run in the debug mode because create_app
#       function by default uses development configuration.
# Note: To access uvicorn running inside the container from the host
#       remember to "link" the exposed port
#       eg. docker run --rm -it -p 8000:8000 $(docker build -q .)
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5000" ,"--factory", "job_tracker:create_app"]
# -- end def final_image --
