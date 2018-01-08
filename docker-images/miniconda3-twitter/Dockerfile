############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################
FROM continuumio/miniconda3
ARG credsfile=credentials.yaml

RUN conda install -y pymongo pyyaml
RUN conda install -c conda-forge -y tweepy=3.2.0

WORKDIR /home
RUN git clone https://github.com/kevhen/CryptoCrawler.git
ADD $credsfile /home/CryptoCrawler/twitter-listener/credentials.yaml

WORKDIR /home/CryptoCrawler/twitter-listener

CMD python streamlistener.py
