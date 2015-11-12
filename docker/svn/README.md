docker create -v /svn --name svndata ubuntu:14.04 /bin/true

docker run -d --volumes-from svndata --name=svn_kiribati svn:latest

docker build -t svn:latest .
docker create -l svn_kiribati --name=svn_kiribati -p=3690:3690 svn:latest
start svn_kiribati
