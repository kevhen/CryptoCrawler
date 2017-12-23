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
`mkdir ~/mongodb`

### Start
`docker run --name crypto-mongo -v ~/mongodb:/data/db -d mongo:jessie`

## Microservice 2: Twitter Stream Listener
* Based on Anaconder Docker Image
* Storing the Tweets into Mongo DB

### Setup
Build Docker:
`cd docker-images/anaconda3`
`sudo docker build -t custom_anaconda3 .`

### Start
Start Container and bash into it:
`docker run -i --name twitter-listener -d custom_anaconda3 /bin/bash`

TODO: Start Container and start stream listener
`docker run --name twitter-listener -v ~/coding/CryptoCrawler/twitter-listener:~/twitter-listener -d custom_anaconda3`

Bash into Container:
`docker exec -t -i twitter-listener /bin/bash`
