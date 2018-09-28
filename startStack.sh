#!/bin/bash

# Exit on first error, print all commands.
set -ev

START_TIMEOUT=15

#Detect architecture
ARCH=`uname -m`

# Grab the current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#

ARCH=$ARCH docker-compose -f docker-compose.yml down
ARCH=$ARCH docker-compose -f docker-compose.yml up -d

# wait for Stack to start
# incase of errors when running later commands, issue export START_TIMEOUT=<larger number>
echo ${START_TIMEOUT}
sleep ${START_TIMEOUT}
