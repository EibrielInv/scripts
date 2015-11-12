FROM ubuntu:14.04
MAINTAINER Eibriel <eibriel@eibriel.com>

RUN apt-get update
RUN apt-get install -y subversion

RUN groupadd svn
RUN useradd -g svn svn

RUN mkdir /svn
#RUN mkdir /svn/kiribati

RUN chown svn:svn /svn
RUN chmod g+w /svn
RUN chmod g+s /svn

ADD init.sh /init.sh

EXPOSE 3690
VOLUME /svn

USER svn

CMD ["/init.sh"]
