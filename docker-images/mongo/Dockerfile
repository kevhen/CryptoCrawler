############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################
FROM mongo:jessie

ADD https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/mongo/mongodb-fix.service /etc/systemd/system/mongodb-fix.service
RUN systemctl daemon-reload
RUN systemctl enable mongodb-fix
