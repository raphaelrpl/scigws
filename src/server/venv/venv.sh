#!/bin/bash

set -e  # If occur any error, exit

function to_console {
    echo -e "\n*** $1 ***\n"
}

cd $(dirname $0) && cd ..


virtualenv venv --system-site-packages --python=python2.7

echo "Creating virtualenv..."
source venv/bin/activate

to_console "Installing lxml lib..."
case `uname` in
  Linux )
     LINUX=1
     which yum && { echo "**** Operational System: CentOS ****";sudo yum install libxslt-devel libxml2-devel; }
     which apt-get && { echo "**** Operational System: Ubuntu ****";sudo apt-get install libxml2-dev libxslt-dev python-dev; }
     ;;
     * )
     ;;
esac

to_console "Checking up dependencies"
if [ ! -z "$1" ]
    then
        to_console "Running with proxy "$1
        pip install -r venv/requirements.txt --proxy=$1
    else
        to_console 'Runing with no proxy'
        pip install -r venv/requirements.txt
fi
