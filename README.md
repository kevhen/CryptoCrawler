# Presentation
For the presentation, we use [GitPitch](https://gitpitch.com/),
a Markdown Presentation Service, that can be accessed via URL
https://gitpitch.com/kevhen/CryptoCrawler/master.
For Slide-Styling see [Wiki](https://github.com/gitpitch/gitpitch/wiki/Slideshow-Settings)

# Architecture
* I propose a Microservice Architecture: Stateless Docker Containers,
which are configured via a config.yaml file.

## Microservice 1: Mongo DB
* Serving as data storage
* DB is persisted on a Docker Volume
* **No credentials configured, only listen to localhost!!**

### Setup
Create Directory for Persistent Data. On VM:
* `mkdir /data/mongodb`

### Start
Run Docker Container:
* First time:  `docker run --name crypto-mongo -t -v /data/mongodb:/data/db -d mongo:jessie`
* Then: `docker start crypto-mongo`

Useful command:
* Bash into container `docker exec -it crypto-mongo /bin/bash`

## Microservice 2: Twitter Stream Listener
* Based on  Docker Image
* Storing the Tweets into Mongo DB
* Configuration via `config.yaml` in `/CryptoCrawler/twitter-listener` in Repo, with words to listen for, divided into sections (will be used to store tweets in different mongo-collections.)

### Setup
Build Docker:
* `cd /data/`
* Download Dockerfile: `wget https://raw.githubusercontent.com/kevhen/CryptoCrawler/master/docker-images/anaconda3/Dockerfile`
* Create `credentials.yaml` in `/data/` with Twitter credentials.
* Build container: `sudo docker build --build-arg credsfile=./credentials.yaml -t custom_anaconda3 .`

### Start
Start Container:
* First time: `docker run -t -i --name twitter-listener --link crypto-mongo:mongo  -d custom_anaconda3`
* Then: `docker start twitter-listener`

Useful commands
* Attach: `docker attach twitter-listener`
* Detach without closing: `CTRL + p, CTRL +q`

## Microservice 3: Crypto Price Crawler
* We will probably use the [Cryptocompare](https://www.cryptocompare.com/api)-API to retrieve the current and historic prices of the currencies.
* We will probably use the [Cryptocompare](https://www.cryptocompare.com/api)-API to retrieve the current and historic prices of the currencies.

# Setup AWS
## VM Setup
- t2.micro
- AMI: ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20171121.1 (ami-aa2ea6d0)
- root: 8GB
- EBS: 16GB
- open ssh (ip whitelist)
- open http

## Server Setup
- Format EBS Drive: `sudo mkfs -t ext4 /dev/xvdb`
- Make mount-point: `sudo mkdir /data`
- Backup fstab: `sudo cp /etc/fstab /etc/fstab.orig`
- Add new line to fstab: `sudo nano /etc/fstab` <br>
  `/dev/xvdb /data ext4 defaults,nofail 0 2`
- Apply new mountpoints: `sudo mount -a`
- Install docker: `sudo apt-get install docker.io`
- Add user to docker-group: `sudo usermod -a -G docker ubuntu`

## Crawler Setup
- `cd \data`
- `git clone https://github.com/kevhen/CryptoCrawler`
- `mkdir mongodb`

## Start Crawler
- Start Docker for mongo: `docker run --name crypto-mongo -v /data/mongodb:/data/db -d mongo:jessie`
- Start Docker for stream listener: `docker run -t -i --name twitter-listener --link crypto-mongo:mongo -d custom_anaconda3 /bin/bash`
