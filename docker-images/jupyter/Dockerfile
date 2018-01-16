############################################################
# Dockerfile to build Miniconda3 container images
# and install additional packages
############################################################
FROM jupyter/scipy-notebook:0b3ec811c968

USER root
RUN conda install -y pymongo pyastronomy
