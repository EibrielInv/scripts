docker run --name wiki-mysql \
    -e MYSQL_DATABASE=ideasfij_kiriwiki \
    -e MYSQL_USER=ideasfij_kiriwik \
    -v /home/kiribati/Documentos/0_NEW_SERVER/mysql:/var/lib/mysql \
    -d mysql:latest

docker run --name wiki-mysql \
    -e MYSQL_ROOT_PASSWORD=passwd \
    -e MYSQL_DATABASE=database \
    -e MYSQL_USER=user \
    -e MYSQL_PASSWORD="password" \
    -d mysql:latest

docker build -t wiki:latest .
docker create --link=wiki-mysql:wiki-mysql -l=wiki \
    --name=wiki -p=8081:80 \
    -v=/home/kiribati/Documentos/0_NEW_SERVER/wiki:/var/www/html/wiki wiki:latest
docker start wiki

mysql -uideasfij_kiriwik -p ideasfij_kiriwiki < db_backup.dump

docker run -it --link some-mysql:mysql --rm mysql sh -c 'exec mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" -uroot -p"$MYSQL_ENV_MYSQL_ROOT_PASSWORD"'
