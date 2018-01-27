############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################
FROM mongo:jessie

RUN sudo apt-get install sysfsutils
ADD https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/mongo/rc.local /etc/sysfs.conf
