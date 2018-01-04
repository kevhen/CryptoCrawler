> **CryptoCrawler** - Crawling information about Crypto Currencies from the Web, analyze them and present them in a Web-Dashboard. A project from a course at university of media, stuttgart.

<br>

### Table of Contents
<!-- TOC depthFrom:1 depthTo:2 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Documentation & Presentation](#documentation-presentation)
- [Architecture](#architecture)
- [Setup AWS](#setup-aws)
	- [VM Setup](#vm-setup)
	- [Server Setup](#server-setup)
- [Microservices](#microservices)
	- [Microservice 1: Mongo DB](#microservice-1-mongo-db)
	- [Microservice 2: Twitter Stream Listener](#microservice-2-twitter-stream-listener)
	- [Microservice 3: Crypto Price Crawler](#microservice-3-crypto-price-crawler)
	- [Microservice 4: Jupyter Notebook](#microservice-4-jupyter-notebook)
	- [Microservice 5: Dashboard](#microservice-5-dashboard)
- [Useful info & commands](#useful-info-commands)
	- [Docker](#docker)
	- [Maintenance](#maintenance)

<!-- /TOC -->

# Documentation & Presentation
**Documentation**
- Inline (Code Comments)
- README.md (Infos about Setup & Operations)
- Presentation (Ideas, Results, Learnings)

**Presentation**
- We use [GitPitch](https://gitpitch.com/), a Markdown Presentation Service
- Access via: https://gitpitch.com/kevhen/CryptoCrawler/master ("master" can be replaced by other branch-name)
- About Slide-Styling see [Wiki](https://github.com/gitpitch/gitpitch/wiki/Slideshow-Settings)

# Architecture
**Microservice Architecture**
- Stateless
- One Docker Container per Microservice
- Configuration via config.yaml file

**Hosting**
- AWS (using free tier)

# Setup AWS
## VM Setup
- t2.micro
- AMI: ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20171121.1 (ami-aa2ea6d0)
- root: 15GB
- EBS: 16GB
- open ssh (ip whitelist)
- open http
- open tcp 8888 (for jupyter notebook. ip whitelist)

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

# Microservices
## Microservice 1: Mongo DB
**Description:**
- Serving as data storage
- DB is persisted on a Docker Volume
- **No credentials configured, only listen to localhost!!**

**Build:**
- Create Directory for Persistent Data. On VM: `mkdir /data/mongodb`
- No further setup needed, as we use Container from official Docker Repo.

**Run:**
- First time:  `docker run --name crypto-mongo -t -v /data/mongodb:/data/db -d mongo:jessie`
- Then: `docker start crypto-mongo`

## Microservice 2: Twitter Stream Listener
**Description:**
- Based on continuumio/miniconda3 Docker Image
- Storing the Tweets into Mongo DB
- Configuration via `config.yaml` in `/CryptoCrawler/twitter-listener` in Repo, with words to listen for, divided into sections (will be used to store tweets in different mongo-collections.)

**Build:**
- `cd /data/`
- Download Dockerfile: `wget https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/miniconda3-twitter/Dockerfile`
- Create `credentials.yaml` in `/data/` with Twitter credentials.
- Build: `sudo docker build --build-arg credsfile=./credentials.yaml -t miniconda3-twitter .`

**Run:**
- First time: `docker run -t -i --name crypto-twitter-listener --link crypto-mongo:mongo  -d miniconda3-twitter`
- Then: `docker start crypto-twitter-listener`

## Microservice 3: Crypto Price Crawler
**Description:**
- Based on jupyter/scipy-notebook Docker Image
- We will probably use the [Cryptocompare](https://www.cryptocompare.com/api)-API to retrieve the current and historic prices of the currencies.
- We will probably use the [Cryptocompare](https://www.cryptocompare.com/api)-API to retrieve the current and historic prices of the currencies.

## Microservice 4: Jupyter Notebook
**Description:**
- Run **Jupyter Notebook with Python 3** for ad-hoc analyzes and testing
- Includes scipy-stack + pymongo
- Password & IP on whitelist needed for access

**Build:**
- Build: `sudo docker build https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/jupyter/Dockerfile -t jupyter`

**Run:**
- First time: `docker run -d --link crypto-mongo:mongo --name crypto-jupyter -v /data/notebooks:/home/jovyan/work -p 8888:8888 jupyter start-notebook.sh --NotebookApp.password='sha1:f6a0093ff7ca:be25a6064ba30e37265b0f800cbb925c636cc4fe'`
- Then: `docker start crypto-jupyter`

**Access Notebook:**
- Via AWS public DNS-Name + :8888. E.g.: https://ec2-34-227-176-103.compute-1.amazonaws.com:8888
- The DNS-Name will change! Find out current name via AWS Console, or use command on VM: `hostname -f`

## Microservice 5: Dashboard
- Based on continuumio/miniconda3 Docker Image
- Exposes Web-Dashboard via Port 8050
- Configuration via `config.yaml` in `/CryptoCrawler/twitter-listener` in Repo, with words to listen for, divided into sections (will be used to store tweets in different mongo-collections.)

**Build:**
- `cd /data/`
- Download Dockerfile: `wget https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/miniconda3-dash/Dockerfile`
- Build: `sudo docker build -t miniconda3-dash .`

**Run:**
- First time: `docker run -t -i -p 8050:8050 --name crypto-dash --link crypto-mongo:mongo -d miniconda3-dash`
- Then: `docker start crypto-dash`

## Microservice 5: Dashboard
- Based on continuumio/miniconda3 Docker Image
- Exposes Web-Dashboard via Port 8050
- Configuration via `config.yaml` in `/CryptoCrawler/twitter-listener` in Repo, with words to listen for, divided into sections (will be used to store tweets in different mongo-collections.)

### Setup
Build Container:
- `cd /data/`
- Download Dockerfile: `wget https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/miniconda3-dash/Dockerfile`
- Build: `sudo docker build -t miniconda3-dash .`

### Start
Run Container:
- First time: `docker run -t -i -p 8050:80 --name crypto-dash --link crypto-mongo:mongo -d miniconda3-dash`
- Then: `docker start crypto-dash`

# Useful info & commands

## Docker
**Cleanup Docker:**
- `docker system prune -a`

**Attach/Detach Container:**
- `docker attach container_name`
- Detach without closing: `CTRL + p, CTRL +q`
- Bash into container: `docker exec -it container_name /bin/bash`

**Connect to MongoDB in Container from Host:**
- Find out IP address of mongo-container: `docker inspect $CONTAINER_NAME | grep IPAddress`
- Use that IP-Address in MongoDB Client

## Maintenance
**Show size of MongoDB Directory:**
- `sudo du -sh /data/mongodb`
