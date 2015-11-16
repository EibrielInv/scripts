docker run --name tactic-postgres -e POSTGRES_PASSWORD=postgres \
    -v /home/kiribati/Documentos/0_NEW_SERVER/postgres/data:/var/lib/postgresql/data \
    -v /home/kiribati/Documentos/0_NEW_SERVER/postgres/backup:/backup \
    -d postgres:latest

# RESTORE DATABASE

sudo docker run -it --link tactic-postgres:postgres \
        -v /home/kiribati/Documentos/0_NEW_SERVER/postgres/backup:/backup \
        --rm postgres \
        sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres -f /backup/tactic_dump postgres'

# RUN TACTIC

docker build -t tactic:latest .
docker create --link=tactic-postgres:tactic-postgres -l tactic --name=tactic -p=8080:80 \
        -v /home/kiribati/Documentos/0_NEW_SERVER/tactic_files/assets:/assets \
        tactic:latest
docker start tactic
