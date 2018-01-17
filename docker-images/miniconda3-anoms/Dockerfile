############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################
FROM continuumio/miniconda3

RUN conda install -y flask
RUN pip install pyastronomy

WORKDIR /home
RUN git clone https://github.com/kevhen/CryptoCrawler.git

WORKDIR /home/CryptoCrawler/anomaly-detection

CMD python esd.py
