#!/bin/bash

if [ ! -d "/svn/kiribati" ];
then
    mkdir /svn/kiribati
    cd /svn/kiribati
    svn checkout svn://$SVN_KIRIBATI_PORT_3690_TCP_ADDR .
fi

# RUN SERVER

python /bam/webservice/bam/manage.py runserver -h 0.0.0.0
