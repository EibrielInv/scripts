docker build -t bam:latest .
docker create --link=svn_kiribati:svn_kiribati -l bam_kiribati --name=bam_kiribati -p=5000:5000 \
    -v /svn/bam_svn:/svn/kiribati \
    -v /svn/bam_db:/db
    -v /svn/bam_upload:/upload
    bam:latest

docker start bam_kiribati



bam_cli.py init http://127.0.0.1:5000/kiribati

http://127.0.0.1:5000/admin

on settings add:
Name: kiribati
Repository Path: /svn_kiribati
Upload Path: /test

Settings:
1)
Name: svn_password
Value: mypasswd
Data Type: string
2)
Name: svn_default_user
Value: myname
Data Type: string
