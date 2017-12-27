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
Create Directory for Persistent Data:
* `mkdir ~/mongodb`

### Start
Run Docker Container:
* `docker run --name crypto-mongo -v ~/mongodb:/data/db -d mongo:jessie`

## Microservice 2: Twitter Stream Listener
* Based on  Docker Image
* Storing the Tweets into Mongo DB

### Setup
Build Docker:
* `cd docker-images/anaconda3`
* `sudo docker build -t custom_anaconda3 .`

Clone Repo to get python code for twitter-listener:
* `git clone https://github.com/kevhen/CryptoCrawler.git`

Configure:
* Create `credentials.yaml` in `/CryptoCrawler/twitter-listener` with Twitter credentials.
* Create `config.yaml` in `/CryptoCrawler/twitter-listener` with words to listen for, divided into sections (will be used to store tweets in different mongo-collections.)


### Start
Start Container (and bash), path to `/CryptoCrawler/twitter-listener` has to be adjusted:
* `docker run -t -i --name twitter-listener -v PATHTO/CryptoCrawler/twitter-listener:/home/twitter-listener -d custom_anaconda3  /bin/bash`
* For Holger: `docker run -t -i --name twitter-listener --link crypto-mongo:mongo -v ~/coding/CryptoCrawler/twitter-listener:/home/twitter-listener -d custom_anaconda3 /bin/bash`

Bash into Container:
* `docker exec -t -i twitter-listener /bin/bash`

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
- Start Docker for stream listener: `docker run -t -i --name twitter-listener --link crypto-mongo:mongo -v /data/CryptoCrawler/twitter-listener:/home/twitter-listener -d custom_anaconda3 /bin/bash`

