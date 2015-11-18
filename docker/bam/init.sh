#!/bin/bash

if [ ! -f /db/bam.db ]
then
    python webservice/bam/manage.py db init
    python webservice/bam/manage.py db upgrade
    python webservice/bam/manage.py create_all_tables
fi

# RUN SERVER

python /bam/webservice/bam/manage.py runserver -h 0.0.0.0
