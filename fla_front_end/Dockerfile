# Docker community maintained image:
# - based on the slimmed down version of Debian 12 (aka 'bookworm', EOL in mid 2028)
# - with python 3.11.7 (last currently available version of the 3.11 series)
FROM python:3.11.7-slim-bookworm

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
COPY --chown=regularuser pip-requirements.txt pyproject.toml constraints.txt ./

# Install globally pinned pip version
# and upgrade setuptools to its latest version to avoid problems.
# Install (normal) dependencies at the versions pinned in the constraints.txt
# (do not create cache directory for the downloaded dependencies as
#  they won't be needed for anything else - reduces image size)
# (This command DOES NOT install project's package itself. When the
#  project changes (new features/bug fixes) this layer, containing
#  only the dependencies, will not have to get rebuild).
RUN python -m pip install --no-cache-dir -r pip-requirements.txt && \
  python -m pip install --no-cache-dir --upgrade setuptools && \
  python -m pip install --no-cache-dir -c constraints.txt "."

# Copy over project's sources
COPY --chown=regularuser .env ./
COPY --chown=regularuser src/ src/

# Install project's package
RUN python -m pip install . -c constraints.txt

# run whatever needs to be run
CMD ["flask", "--app", "src/job_tracker_frontend", "run", \
  "--host", "0.0.0.0", "--port", "9022"]
