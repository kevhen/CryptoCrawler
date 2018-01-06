> **CryptoCrawler** - Crawling information about Crypto Currencies from the Web, analyze them and present them in a Web-Dashboard. A project from a course at university of media, stuttgart.

<br>

# Table of Contents

<!-- TOC depthFrom:1 depthTo:2 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Table of Contents](#table-of-contents)
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
	- [Microservice 6: LDA Topic Identification](#microservice-6-lda-topic-identification)
- [Useful info & commands](#useful-info-commands)
	- [Docker](#docker)
	- [Docker Compose](#docker-compose)
	- [Maintenance](#maintenance)
- [Issues](#issues)

<!-- /TOC -->

 # Documentation & Presentation

**Documentation**

- Inline (Code Comments)
- README.md (Infos about Setup & Operations)
- Presentation (Ideas, Results, Learnings)

**Presentation**

- We use [GitPitch](https://gitpitch.com/), a Markdown Presentation Service
- Access via: <https://gitpitch.com/kevhen/CryptoCrawler/master> ("master" can be replaced by other branch-name)
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

- t2.medium
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
- Add new line to fstab: `sudo nano /etc/fstab`<br>
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

- First time: `docker run --name crypto-mongo -t -v /data/mongodb:/data/db -d mongo:jessie`
- Then: `docker start crypto-mongo`

## Microservice 2: Twitter Stream Listener

**Description:**

- Storing the Tweets into Mongo DB
- Configuration via `/CryptoCrawler/config.yaml` in Repo, with words to listen for, divided into sections (will be used to store tweets in different mongo-collections.)

**Build:**

- `cd /data/`
- Download Dockerfile: `wget https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/miniconda3-twitter/Dockerfile`
- Create `credentials.yaml` in `/data/` with Twitter credentials.
- Build: `sudo docker build --build-arg credsfile=./credentials.yaml -t miniconda3-twitter .`

**Run:**

- First time: `docker run -t -i --name crypto-twitter-listener --link crypto-mongo:mongo -d miniconda3-twitter`
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

- `sudo docker build https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/jupyter/Dockerfile -t custom_jupyter`

**Run:**

- First time: `docker run -d --link crypto-mongo:mongo --name crypto-jupyter -v /data/notebooks:/home/jovyan/work -p 8888:8888 custom_jupyter start-notebook.sh --NotebookApp.password='sha1:f6a0093ff7ca:be25a6064ba30e37265b0f800cbb925c636cc4fe'`
- Then: `docker start crypto-jupyter`

**Access Notebook:**

- Via AWS public DNS-Name + :8888\. E.g.: <https://ec2-34-227-176-103.compute-1.amazonaws.com:8888>
- The DNS-Name will change! Find out current name via AWS Console, or use command on VM: `hostname -f`

## Microservice 5: Dashboard

**Description:**

- Exposes Web-Dashboard via Port 8050
- Configuration via `/CryptoCrawler/config.yaml` in Repo, with words to listen for, divided into sections (will be used to store tweets in different mongo-collections.)

**Build:**

- `sudo docker build https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/miniconda3-dash/Dockerfile -t miniconda3-dash`

**Run:**

- First time: `docker run -t -i -p 8050:8050 --name crypto-dash --link crypto-mongo:mongo -d miniconda3-dash`
- Then: `docker start crypto-dash`

**View Dashboard:**

- Via AWS public DNS-Name + :8050\. E.g.: <https://ec2-34-227-176-103.compute-1.amazonaws.com:8050>
- The DNS-Name will change! Find out current name via AWS Console, or use command on VM: `hostname -f`

## Microservice 6: LDA Topic Identification

**Description:**

- Exposes Web-Service to Port 5000
- Takes collection name, start + end timestamps and desired topic count, gives back topics as a list of words with probablility values

**Build:**

- `sudo docker build https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/miniconda3-topics/Dockerfile -t miniconda3-topics`

**Run:**

- First time: `docker run -t -i -p 5000:5000 --name crypto-topics --link crypto-mongo:mongo -d miniconda3-topics`
- Then: `docker start crypto-topics`

**Query:**

- Example Call: <http://0.0.0.0:5000/lda?collection=bitcoin&start=1515082825836&end=1515082840114&topics=6>
- Example Result:

  ```json
  {
  "tweet_count": 48,
  "topics": [
      [["bitcoin", 0.06317], ["forget", 0.02357], ["cryptocurrency", 0.01791], ["cypherpunks", 0.01791], ["dont", 0.01791], ["blockchain", 0.01791], ["birthday", 0.01791], ["keiser", 0.01791], ["happy", 0.01791], ["ethereum", 0.01225], ["fintech", 0.01225], ["ico", 0.01225], ["seo", 0.0066], ["smm", 0.0066], ["zovio", 0.0066], ["webhosting", 0.0066], ["website", 0.0066], ["meaningful", 0.0066], ["way", 0.0066], ["retargeting", 0.0066]],
      [["bitcoin", 0.02482], ["ethereum", 0.01291], ["market", 0.01291], ["night", 0.01291], ["must", 0.01291], ["each", 0.01291], ["dustinlyle", 0.01291], ["intended", 0.01291], ["cheaper", 0.01291], ["then", 0.01291], ["bought", 0.01291], ["away", 0.01291], ["607", 0.01291], ["2011", 0.01291], ["makeiser", 0.01291], ["much", 0.01291], ["says", 0.01291], ["giving", 0.01291], ["btc", 0.01291], ["dont", 0.01291]],
      [["charge", 0.01682], ["able", 0.01682], ["current", 0.00906], ["one", 0.00906], ["centralized", 0.00906], ["ripple", 0.00906], ["mmn013", 0.00906], ["criptofin", 0.00906], ["everyone", 0.00906], ["participates", 0.00906], ["saying", 0.00906], ["software", 0.00906], ["witotrader", 0.00906], ["well", 0.00906], ["incentives", 0.00906], ["work", 0.00906], ["alter", 0.00906], ["providersregulatorsthe", 0.00906], ["treywilder2002", 0.00906], ["novogratz", 0.00906]],
      [["people", 0.01283], ["edkrassen", 0.01283], ["could", 0.01283], ["ico", 0.01283], ["blockchain", 0.01283], ["ledger", 0.01283], ["cryptocurrencies", 0.01283], ["rich", 0.01283], ["help", 0.01283], ["crypto", 0.01283], ["bitcoin", 0.01282], ["safe", 0.00691], ["better", 0.00691], ["buy", 0.00691], ["via", 0.00691], ["macys", 0.00691], ["ripple", 0.00691], ["use", 0.00691], ["cryptocurrency", 0.00691], ["giftzcard", 0.00691]],
      [["crypto", 0.0271], ["bitcoin", 0.02708], ["btc", 0.02059], ["one", 0.01409], ["cryptoneti", 0.01408], ["rubinreport", 0.01408], ["basically", 0.01408], ["benshapiro", 0.01408], ["course", 0.01408], ["impossible", 0.01408], ["making", 0.01408], ["sitdown", 0.01408], ["teamyoutube", 0.01408], ["theyre", 0.01408], ["demonetized", 0.01408], ["2018", 0.01408], ["predictions", 0.01408], ["tokenized", 0.01408], ["high\u2013", 0.00758], ["ethe", 0.00758]],
      [["bitcoin", 0.04443], ["trump", 0.01723], ["amp", 0.01179], ["get", 0.01179], ["breaking", 0.01179], ["bitcoincash", 0.01179], ["systems", 0.01179], ["store", 0.01179], ["financial", 0.01179], ["total", 0.00635], ["things", 0.00635], ["coinflowio", 0.00635], ["days", 0.00635], ["returns", 0.00635], ["unpatriotic", 0.00635], ["wolff", 0.00635], ["per", 0.00635], ["automated", 0.00635], ["lending", 0.00635], ["murthaburke", 0.00635]]
  ],
  "num_topics": 6}
  ```

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

## Docker Compose

**Build & run containers in background:**

- `docker-compose up -d`

**See output of containers:**

- `docker-compose logs -f` for all output or
- `docker-compose logs -f $CONTAINER_NAME` for output of some containers

## Maintenance

**Show size of MongoDB Directory:**

- `sudo du -sh /data/mongodb`

# Issues

**Things that could be improved, if we had more time:**

- Data Loading for Dash is not efficient. If multiple users connect to Dash, performance goes down a lot.
