#!/bin/bash

umask 002

# RUN SERVER

svnserve --daemon --foreground --root /svn/kiribati
