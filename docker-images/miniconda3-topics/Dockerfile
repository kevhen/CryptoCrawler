############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################
FROM continuumio/miniconda3

RUN conda install -y pymongo pyyaml flask nltk gensim pandas
RUN conda install -c conda-forge webargs

WORKDIR /home
RUN git clone https://github.com/kevhen/CryptoCrawler.git

WORKDIR /home/CryptoCrawler/topic-model

CMD python lda.py
