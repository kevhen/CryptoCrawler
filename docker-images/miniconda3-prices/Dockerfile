############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################
FROM continuumio/miniconda3

RUN conda install -y pymongo pyyaml
RUN conda install -c conda-forge -y tweepy
RUN conda install -c gomss-nowcast schedule

WORKDIR /home
RUN git clone https://github.com/kevhen/CryptoCrawler.git

WORKDIR /home/CryptoCrawler/crypto-price-crawler

CMD python pricelistener.py
