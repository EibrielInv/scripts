docker build -t server-proxy:latest .
docker create --link=wiki:wiki --link=eibriel:eibriel --link=rbu:rbu --link=rdany-web:rdany-web -l=proxy --name=proxy -p=80:80 server-proxy:latest
docker start proxy
