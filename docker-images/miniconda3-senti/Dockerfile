############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################
FROM continuumio/miniconda3

RUN conda install -y pymongo pyyaml nltk pandas

WORKDIR /home
RUN git clone https://github.com/kevhen/CryptoCrawler.git

WORKDIR /home/CryptoCrawler/add-sentiment

CMD while true; do python sentiment.py; done
