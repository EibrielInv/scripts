#!/bin/bash

echo 'Start Database Configuration'

python /database_conf.py

echo 'End Database Configuration'

echo 'Run Apache2'

/usr/sbin/apache2

echo 'Run TACTIC'

sudo -E -u www-data python /home/apache/tactic/src/bin/monitor.py

echo 'DONE'
