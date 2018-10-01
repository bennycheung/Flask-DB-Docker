#!/bin/bash

cd ..
echo "Reseting database to clean state"
python manage.py createdb
echo "Creating super user admin:admin"
python manage.py adduserpass admin admin

echo "Done."
