#!/bin/bash

# Exit on first error, print all commands.
set -ev

START_TIMEOUT=15

#Detect architecture
ARCH=`uname -m`

# Grab the current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Build all the docker images before starting the stack
cd ${DIR}/busybox
docker build -t starter/postgres_datastore .

cd ${DIR}/db
docker build -t starter/postgres .

cd ${DIR}/starter-api
docker build -t starter/starter-api .
