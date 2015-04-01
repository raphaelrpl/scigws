#!/bin/bash

set -e  # If occur any error, exit

function to_console {
    echo -e "\n*** $1 ***\n"
}

cd $(dirname $0) && cd ..

virtualenv venv

echo "Creating virtualenv..."
source venv/bin/activate

to_console "Checking up dependencies"
if [ ! -z "$1" ]
    then
        to_console "Running with proxy "$1
        pip install -r venv/requirements.txt --proxy=$1
    else
        to_console 'Runing with no proxy'
        pip install -r venv/requirements.txt
fi