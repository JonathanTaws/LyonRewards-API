#!/bin/sh
# Permet de faire un backup de owncloud

DATE=$(date +"%Y%m%d%H%M")
NAME=lyonrewards_api
RESULTPATH=/var/lib/postgresql/backup
DBNAME=lyonrewards

sudo -u postgres bash -c "pg_dump $DBNAME > $RESULTPATH/backup_db_$NAME\_$DATE.sql"
