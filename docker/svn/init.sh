#!/bin/bash

umask 002

if [ ! -d "/svn/kiribati" ];
then

    #mv /svn_tmp/kiribati /svn/kiribati

    #RUN mkdir /svn/kiribati

    chown svn:svn /svn
    chmod g+w /svn
    chmod g+s /svn

    svnadmin create /svn/kiribati

    #password-db = passwd

    echo "[general]" > /svn/kiribati/conf/svnserve.conf
    echo "password-db = passwd" >> /svn/kiribati/conf/svnserve.conf

    echo "myname = mypasswd" >> /svn/kiribati/conf/passwd
fi

# RUN SERVER

#python /bam/webservice/bam/manage.py runserver -h 0.0.0.0
svnserve --daemon --foreground --root /svn/kiribati
