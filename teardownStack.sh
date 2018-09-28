#!/bin/bash

# Exit on first error, print all commands.
set -ev

#Detect architecture
ARCH=`uname -m`

# Grab the current directory.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Shut down the Docker containers for the system tests.
cd "${DIR}"
ARCH=$ARCH docker-compose -f docker-compose.yml kill && docker-compose -f docker-compose.yml down

# Your system is now clean
