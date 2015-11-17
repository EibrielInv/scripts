FROM python:3.5
MAINTAINER Eibriel <eibriel@eibriel.com>

RUN apt-get update
RUN apt-get install -y git subversion

RUN mkdir /bam
WORKDIR /bam
RUN git clone git://git.blender.org/blender-asset-manager.git .

ADD config.py webservice/bam/config.py

RUN pip install -r webservice/requirements.txt

RUN mkdir /db
RUN python webservice/bam/manage.py db init
RUN python webservice/bam/manage.py db upgrade
RUN python webservice/bam/manage.py create_all_tables

ADD init.sh /init.sh

ENV BAM_VERBOSE=bam

WORKDIR /bam
CMD ["/init.sh"]
