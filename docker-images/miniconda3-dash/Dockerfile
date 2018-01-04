############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################
FROM continuumio/miniconda3

RUN conda install -y pymongo pyyaml pandas

RUN pip install dash==0.19.0  # The core dash backend
RUN pip install dash-renderer==0.11.1  # The dash front-end
RUN pip install dash-html-components==0.8.0  # HTML components
RUN pip install dash-core-components==0.15.2  # Supercharged components
RUN pip install plotly --upgrade  # Plotly graphing library used in examples

WORKDIR /home
RUN git clone https://github.com/kevhen/CryptoCrawler.git

WORKDIR /home/dash

CMD python dashboard.py
