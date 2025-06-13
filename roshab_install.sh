#!/usr/bin/env bash

export NXF_VER=24.10.2

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if command_exists nextflow; then
    echo "Nextflow is installed. Current version:"
    nextflow -version
    else
    echo "Install Nextflow before executing this script."
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo "Activate Docker before executing this script."
    exit 1
    else
    echo "Downloading Containers"
    nextflow run main.nf -profile setup -resume
    echo "Containers downloaded successfully."
    rm -rf ./work
    rm -rf .nextflow.log*
    rm -rf .nextflow
fi

if command_exists python3; then
    echo "Python 3 is installed. Current version:"
    python3 --version
    else
    echo "Install Python 3 before executing this script."
    exit 1
fi

if command_exists "python3 -m pip"; then
    echo "pip is installed. Updating..."
    python3 -m pip install --upgrade pip
    else
    echo "Install pip before executing this script."
    exit 1
fi

if command_exists python3 -m venv; then
    echo "Creating virtual environment 'roshab_env'..."
    python3 -m venv roshab_env
    else
    echo "Install venv before executing this script."
    exit 1
fi

source roshab_env/bin/activate
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
deactivate
exit 0
