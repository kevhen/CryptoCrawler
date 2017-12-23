# Presentation
For the presentation, we can use [GitPitch](https://gitpitch.com/),
a Markdown Presentation Service, that can be accessed via URL
https://gitpitch.com/kevhen/CryptoCrawler/master , but we need to set
the repo public first. I created `PITCHME.md` with a default template for the presentation.
We could build on that.

# Architecture
* I propose a Microservice Architecture: Stateless Docker Containers,
which are configured via a config.yaml file.

## Microservice 1: Mongo DB
* Serving as data storage
* DB is persisted on a Docker Volume
* **No credentials configured, only listen to localhost!!**

### Setup
Create Directory for Persistent Data:
*`mkdir ~/mongodb`

### Start
Run Docker Container:
* `docker run --name crypto-mongo -v ~/mongodb:/data/db -d mongo:jessie`

## Microservice 2: Twitter Stream Listener
* Based on Anaconder Docker Image
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
Start Container (and bash):
* Cmd for Holger (adjust path to twitter-listener directory): `docker run -i --name twitter-listener -v ~/coding/CryptoCrawler/twitter-listener:/home/twitter-listener -d custom_anaconda3  /bin/bash`

Bash into Container:
* `docker exec -t -i twitter-listener /bin/bash`
