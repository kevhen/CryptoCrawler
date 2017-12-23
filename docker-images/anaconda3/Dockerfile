############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################

FROM continuumio/miniconda3
RUN conda install -y pymongo pyyaml
RUN conda install -c conda-forge -y tweepy

WORKDIR /home
RUN mkdir twitter-listener
