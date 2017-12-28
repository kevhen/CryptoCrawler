> CryptoCrawler: Crawl Information about Crypto Currencies from the Web, analyze them and present them in a Web-Dashboard.


**Table of Contents**
<!-- TOC depthFrom:1 depthTo:2 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Documentation & Presentation](#documentation-presentation)
- [Architecture](#architecture)
	- [Microservice 1: Mongo DB](#microservice-1-mongo-db)
	- [Microservice 2: Twitter Stream Listener](#microservice-2-twitter-stream-listener)
	- [Microservice 3: Crypto Price Crawler](#microservice-3-crypto-price-crawler)
	- [Microservice 4: Jupyter Notebook](#microservice-4-jupyter-notebook)
- [Setup AWS](#setup-aws)
	- [VM Setup](#vm-setup)
	- [Server Setup](#server-setup)
	- [Microservice Setup & Start](#microservice-setup-start)
- [Useful Info & commands](#useful-info-commands)

<!-- /TOC -->

# Documentation & Presentation
**Documentation**
- Inline (Code Comments)
- README.md (Infos about Setup & Operations)
- Presentation (Ideas, Results, Learnings)

**Presentation**
- We use [GitPitch](https://gitpitch.com/), a Markdown Presentation Service
- Access via: https://gitpitch.com/kevhen/CryptoCrawler/master ("master" can be replaced by other <branch-name>)
- About Slide-Styling see [Wiki](https://github.com/gitpitch/gitpitch/wiki/Slideshow-Settings)

# Architecture
**Microservice Architecture**
- Stateless
- One Docker Container per Microservice
- Configuration via config.yaml file

**Hosting**
- AWS (using free tier)

## Microservice 1: Mongo DB
- Serving as data storage
- DB is persisted on a Docker Volume
- **No credentials configured, only listen to localhost!!**

### Setup
Create Directory for Persistent Data. On VM:
- `mkdir /data/mongodb`

### Start
Run Docker Container:
- First time:  `docker run --name crypto-mongo -t -v /data/mongodb:/data/db -d mongo:jessie`
- Then: `docker start crypto-mongo`

## Microservice 2: Twitter Stream Listener
- Based on  Docker Image
- Storing the Tweets into Mongo DB
- Configuration via `config.yaml` in `/CryptoCrawler/twitter-listener` in Repo, with words to listen for, divided into sections (will be used to store tweets in different mongo-collections.)

### Setup
Build Docker:
- `cd /data/`
- Download Dockerfile: `wget https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/anaconda3/Dockerfile`
- Create `credentials.yaml` in `/data/` with Twitter credentials.
- Build container: `sudo docker build --build-arg credsfile=./credentials.yaml -t custom_anaconda3 .`

### Start
Start Container:
- First time: `docker run -t -i --name twitter-listener --link crypto-mongo:mongo  -d custom_anaconda3`
- Then: `docker start twitter-listener`

## Microservice 3: Crypto Price Crawler
- We will probably use the [Cryptocompare](https://www.cryptocompare.com/api)-API to retrieve the current and historic prices of the currencies.
- We will probably use the [Cryptocompare](https://www.cryptocompare.com/api)-API to retrieve the current and historic prices of the currencies.

## Microservice 4: Jupyter Notebook
Build container:
- `sudo docker build https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/jupyter/Dockerfile -t custom_jupyter`

Start container:
- First time: `docker run -d --link crypto-mongo:mongo --name custom-jupyter -v /data/notebooks:/home/jovyan/work -p 8888:8888 custom_jupyter start-notebook.sh --NotebookApp.password='sha1:f6a0093ff7ca:be25a6064ba30e37265b0f800cbb925c636cc4fe'`
- Then: `docker start custom-jupyter`

# Setup AWS
## VM Setup
- t2.micro
- AMI: ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20171121.1 (ami-aa2ea6d0)
- root: 15GB
- EBS: 16GB
- open ssh (ip whitelist)
- open http
- open tcp 8888 (jupyter notebook)

## Server Setup
**Prepare & mount EBS Drive**
- Format EBS Drive: `sudo mkfs -t ext4 /dev/xvdb`
- Make mount-point: `sudo mkdir /data`
- Backup fstab: `sudo cp /etc/fstab /etc/fstab.orig`
- Add new line to fstab: `sudo nano /etc/fstab` <br>
  `/dev/xvdb /data ext4 defaults,nofail 0 2`
- Apply new mountpoints: `sudo mount -a`#

**Prepare Docker**
- Install docker: `sudo apt-get install docker.io`
- Add user to docker-group: `sudo usermod -a -G docker ubuntu`

## Microservice Setup & Start
see sections above.

# Useful Info & commands
**Cleanup Docker**
- `docker system prune -a`

**Show size of Docker Dir**
- `sudo du -sh \data\mongodb`

**Attach/Detach Container**
- `docker attach container_name`
- Detach without closing: `CTRL + p, CTRL +q`
- Bash into container: `docker exec -it container_name /bin/bash`
