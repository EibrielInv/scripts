FROM ubuntu:14.04
MAINTAINER Eibriel <eibriel@eibriel.com>

RUN apt-get update
RUN apt-get install -y subversion

RUN groupadd svn
RUN useradd -g svn svn

ADD init.sh /init.sh

EXPOSE 3690

USER svn

CMD ["/init.sh"]
