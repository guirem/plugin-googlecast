#!/bin/bash

pip3cmd=$(compgen -ac | grep -E '^pip-?3' | sort -r | head -1)
if [[ -z  $pip3cmd ]]; then     # pip3 not found
    if python3 -m pip -V 2>&1 | grep -q -i "^pip " ; then     # but try other way
        pip3cmd="python3 -m pip"
    fi
fi

if [[ ! -z  $pip3cmd ]]; then     # pip3 found
    echo "-- Updating requirements :"
    echo $(sudo $pip3cmd install -r $1/requirements.txt)
    # echo $(sudo $pip3cmd install -r $1/requirements-nodep.txt --no-deps)
else
    echo "Error: Cound not found pip3 program to update python dependencies !"
fi

BASEDIR="$(dirname "$(dirname "$(readlink -fm "$0")")")"

# make sure htaccess is created
HTACCESS="$BASEDIR/.htaccess"
if [[ ! -f  "$HTACCESS" ]]; then   # htaccess created
    echo "Options +FollowSymLinks\n" >> $HTACCESS
    chown www-data:www-data $HTACCESS
    chmod 644 $HTACCESS
fi

#### JEEDOM 4.2 MIGRATION
# migrate media files from jeedom version prior to 4.2 
if [[ ! -z  $BASEDIR ]]; then   # basedir is not empty

    MIGRATION_SRC=$BASEDIR/localmedia
    MIGRATION_DEST=$BASEDIR/data/media
    if [[ -d "$MIGRATION_SRC" ]]; then
        cp -n $MIGRATION_SRC/* $MIGRATION_DEST
        rm -Rf $MIGRATION_SRC
    fi
    # clean old temp folder symlinkg for jeedom version prior to 4.2 
    OLDTMPDIR=$BASEDIR/tmp
    if [[ -d "$OLDTMPDIR" ]]; then
        rm -f $OLDTMPDIR
    fi

fi

