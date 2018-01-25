############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################
FROM continuumio/miniconda3

RUN conda install -y pymongo pyyaml pandas

RUN pip install flask-jsonpify
RUN pip install flask
RUN pip install flask_restful
RUN pip install AioHTTP

WORKDIR /home
RUN git clone https://github.com/kevhen/CryptoCrawler.git

WORKDIR /home/CryptoCrawler/crypto-api-wrapper

CMD python apiwrapper.py
