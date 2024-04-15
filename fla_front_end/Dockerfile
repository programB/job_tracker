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

# Copy over the project's definition and requirements
# (changing file ownership) but not project sources.
# This is to keep docker layers isolated - a change to source in the
# files will not result in rebuild of this layer.
COPY --chown=regularuser pyproject.toml .flake8 constraints.txt ./

# Instal and upgrade pip and setuptools to latest versions
# Install (normal) dependencies at the versions pinned in the constraints.txt
# (do not create cache directory for the downloaded dependencies as
#  they won't be needed for anything else - reduces image size)
RUN python -m pip install --upgrade pip setuptools && \
  python -m pip install --no-cache-dir -c constraints.txt "."

# Copy over project's sources
COPY --chown=regularuser .env ./
COPY --chown=regularuser src/ src/

# run the application directly from the source tree
CMD ["flask", "--app", "src/job_tracker_frontend", "run", \
  "--host", "0.0.0.0", "--port", "9022"]
