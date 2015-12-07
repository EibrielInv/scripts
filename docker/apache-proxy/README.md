docker build -t server-proxy:latest .
docker create --link=wiki:wiki-mysql -l=proxy --name=proxy -p=80:80
docker start server-proxy
