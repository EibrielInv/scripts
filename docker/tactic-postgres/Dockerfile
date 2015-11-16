FROM postgres:9.4

COPY tactic_dump /tactic_dump

RUN psql -f /tactic_dump postgres
