#!/bin/bash

# Exit on first error, print all commands.
set -ev

#Detect architecture
ARCH=`uname -m`

# Grab the current directory.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Clean up the Docker images for the system.
docker rmi $(docker images starter/* -q)
docker network prune -f
docker volume prune -f

# Your system images are cleaned
