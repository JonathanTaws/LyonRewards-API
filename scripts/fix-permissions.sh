#!/bin/bash
#This script is used to fix the system permissions.
#You must keep this script up to date (new component=new system user=new lines in this script)

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script can be launch with root only."
   exit 1
fi

PATHSCRIPT=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [ ! -f $PATHSCRIPT/scriptparameters ]
then
    echo "The file 'scriptparameters' in the path '$PATHSCRIPT' is not present."
    echo "Without this file, the script can't run apply the right rules."
    echo "Scriptparameters exemple :"
    echo '  SOURCEDIR=lyonRewards'
    echo '  SCRIPTDIR=scripts'
    echo '  SCRIPTDEBUG=false'
    echo '  PROJECTROOTDIR=/var/www/lyonrewards-api'
    echo '  USER=lyonrewards'
    echo '  GROUP=lyonrewards' 
    exit 1
fi

. $PATHSCRIPT/scriptparameters

if [ "$SCRIPTDEBUG" == "true" ]
then
    MODE=echo
else
    MODE=eval
fi

echo "Fix some rights on project subtree"

$MODE "chown -R $USER:$GROUP $PROJECTROOTDIR"
$MODE "find $PROJECTROOTDIR -type d -print0 | xargs -0 chmod 755"
$MODE "find $PROJECTROOTDIR -type f -print0 | xargs -0 chmod 644"
$MODE "find $PROJECTROOTDIR/$SCRIPTDIR -name '*.sh' -type f -print0 | xargs -0 chmod 755"
$MODE "find $PROJECTROOTDIR/$SOURCEDIR/bin/gunicorn_start -type f -print0 | xargs -0 chmod 755"

echo Fix done
