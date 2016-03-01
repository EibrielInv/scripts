docker build -t server-proxy:latest .
docker create --link=wiki:wiki --link=eibriel:eibriel --link=gnusocial:gnusocial --link=rbu:rbu --link=woz:woz -l=proxy --name=proxy -p=80:80 server-proxy:latest
docker start proxy
