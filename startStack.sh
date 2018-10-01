#!/bin/bash

# Exit on first error, print all commands.
set -ev

START_TIMEOUT=10

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

# load initial demo data
docker run --rm -t --network flask-db-docker_default starter/starter-api /bin/bash \
   -c "cd startup && ./resetdb.sh"

docker run --rm -t \
    --network flask-db-docker_default \
    -v `pwd`/starter-api/startup:/app/startup \
    starter/postgres /bin/bash -c \
    "PGPASSWORD=admin psql -h starter-postgres -U admin starter < /app/startup/starter_pxcodes.sql"