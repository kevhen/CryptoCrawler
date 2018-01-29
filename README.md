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
	- [Microservice 4: Crypto Api Wrapper](#microservice-9-crypto-api-wrapper)
	- [Microservice 5: Jupyter Notebook](#microservice-4-jupyter-notebook)
	- [Microservice 6: Dashboard](#microservice-5-dashboard)
	- [Microservice 7: LDA Topic Identification](#microservice-6-lda-topic-identification)
	- [Microservice 8: Anomaly Detection](#microservice-7-anomaly-detection)
	- [Microservice 9: Sentiment Analysis](#microservice-8-sentiment-analysis)
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
- Ports open with ip whitelist (*for debugging only):
    - ssh 22
    - http 80
    - tcp 8888 - Jupyter notebook
    - tcp 8050 - Dashboard
    - *tcp 5000 - Topic Modelling
    - *tcp 5001 - Anomaly Detection

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
- Tune docker by creating config file: `sudo nano /etc/docker/daemon.js`
```json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {"max-size": "5m", "max-file": "2"}
}
```

# Microservices

## Microservice 1: Mongo DB

**Description:**

- Serving as data storage
- DB is persisted on a Docker Volume
- **No credentials configured, only listen to localhost!!**

**Optimize:**

We do lot's of queries based on "timestamp". Let's create an index on this field:
- Bash into mongo: `docker exec -it crypto-mongo /bin/bash`
- Start mongo client: `mongo`
- Select DB: `use cryptocrawl` then `show collections`
- Create Index on timestamp field: `db.$COLLECTIONNAME.createIndex({"timestamp_ms": 1}, {background:true})`
- `db.collection.totalIndexSize()` should fit into RAM

Also run on host:
```bash
echo 1 | sudo tee /sys/kernel/mm/transparent_hugepage/khugepaged/defrag
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag
```

## Microservice 2: Twitter Stream Listener

**Description:**

- Storing the Tweets into Mongo DB
- Configuration via `/CryptoCrawler/config.yaml` in Repo, with words to listen for, divided into sections (will be used to store tweets in different mongo-collections.)

## Microservice 3: Crypto Price Crawler

**Description:**

- Based on jupyter/scipy-notebook Docker Image
- We will probably use the [Cryptocompare](https://www.cryptocompare.com/api)-API to retrieve the current and historic prices of the currencies.

## Microservice 4: Crypto Api Wrapper

**Description:**
- Wraps the Histo-APIs of [Cryptocompare](https://www.cryptocompare.com/api) to use [HistoMinute](https://www.cryptocompare.com/api#-api-data-histominute-), [HistoHour](https://www.cryptocompare.com/api#-api-data-histohour-) and [HistoDay](https://www.cryptocompare.com/api#-api-data-histoday-) to a single API
- Parses all responses to the format required for the dashboard

- Returns a number of random tweets for a topic and a certain timespan to later show them in the Dashboard

**Access the API:**

URL: AWS public DNS-Name/container name + :8060

GET: /price

URL-Parameters:

| Parameter   | Values | Default   | Description  |
|---|---|---|---|
| coin  | ETH, BTC, IOT  | BTC   | Defines the coin for which the prices will be retrieved  |
| currency  | EUR, USD  | EUR   | Defines the currency in which the coin price will be returned  |
| from  | timestamp in ms   | - | Start of the requested timespan  |
| to  | timestamp in ms    | current time   | End of the requested timespan   |
| step   | day, hour, minute   | day   | Step size between two returned price values   |

example: http://********:8060/price?coin=BTC&currency=EUR&from=1516974329398&to=1516974379822&step=day

GET: /tweets

URL-Parameters:

| Parameter   | Values | Default   | Description  |
|---|---|---|---|
| amount  | amount of tweets as an int | 20   | Defines the amount of tweets that are retrieved  |
| topics  | ETH, BTC, IOT  | ETH, BTC, IOT    | Comma separated list of topics for which the tweets are returned  |
| from  | timestamp in ms   | - | Start of the requested timespan  |
| to  | timestamp in ms    | current time   | End of the requested timespan   |

example: http://********:8060/tweets?amount=30&topics=ETH,BTC&from=1516974329398&to=1516974379822&

## Microservice 5: Jupyter Notebook

**Description:**

- Run **Jupyter Notebook with Python 3** for ad-hoc analyzes and testing
- Includes scipy-stack + pymongo
- Password & IP on whitelist needed for access

**Access Notebook:**

- Via AWS public DNS-Name + :8888\. E.g.: <https://ec2-34-227-176-103.compute-1.amazonaws.com:8888>
- The DNS-Name will change! Find out current name via AWS Console, or use command on VM: `hostname -f`

## Microservice 6: Dashboard

**Description:**

- Exposes Web-Dashboard via Port 8050
- Configuration via `/CryptoCrawler/config.yaml` in Repo, with words to listen for, divided into sections (will be used to store tweets in different mongo-collections.)

**View Dashboard:**

- Via AWS public DNS-Name + :8050\. E.g.: <https://ec2-34-227-176-103.compute-1.amazonaws.com:8050>
- The DNS-Name will change! Find out current name via AWS Console, or use command on VM: `hostname -f`

## Microservice 7: LDA Topic Identification

**Description:**

- Exposes Web-Service to Port 5000
- Takes collection name, start + end timestamps and desired topic count, gives back topics as a list of words with probablility values

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

## Microservice 8: Anomaly Detection

**Description:**

- Exposes Web-Service to Port 5001
- Takes a list of values of a timeseries, together with a frequency value and p value.
- Responses the indexes of the anomal values in the list

**Query:**
- Example POST body to `http://localhost:5001/esd`
```json
{
"ary": [112, 118, 132, 129, 121, 135, 148, 148, 136, 119, 104, 118, 115, 126,
 141, 135, 125, 149, 170, 170, 158, 133, 114, 140, 145, 150, 178, 163, 172,
 178, 199, 199, 184, 162, 146, 166, 171, 180, 193, 181, 183, 218, 230, 242,
 209, 191, 172, 194, 196, 196, 236, 235, 229, 243, 264, 272, 237, 211, 180,
 201, 204, 188, 235, 227, 234, 264, 302, 293, 259, 229, 203, 229, 242, 233,
 267, 269, 270, 315, 364, 347, 312, 274, 237, 278, 284, 277, 317, 313, 318,
 374, 413, 405, 355, 306, 271, 306, 315, 301, 356, 348, 355, 422, 465, 467,
 404, 347, 305, 336, 340, 318, 362, 348, 363, 435, 491, 505, 404, 359, 310,
 337, 360, 342, 406, 396, 420, 472, 548, 559, 463, 407, 362, 405, 417, 391,
 419, 461, 472, 535, 622, 606, 508, 461, 390, 432],
"freq": 12,
"p": 0.95
}
```
- Example Response:
```

```

## Microservice 9: Sentiment Analysis

**Description:**
- Used to add sentiment information to all tweets in MongoDB
- Constently queries MongoDB for Tweets without sentiment/score (every 30sec)
- Calculates sentiment & score and stores them to MongoDB
- Very simple algo: Just look for pos/neg words from [a well known list for financial sentiment analysis](https://www3.nd.edu/~mcdonald/Word_Lists.html).
- The **Score** value is: (count of positive words) - (count of negative words)
- **Sentiment** can be "neg" (score < 0), "pos" (score > 0) or "neu" (score = 0)




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

**Force Rebuild all containers**

- `docker-compose build --no-cache`


## Maintenance

**Show size of MongoDB Directory:**

- `sudo du -sh /data/mongodb`

**Show Top 10 largest directories:**

- `du -a / | sort -n -r | head -n 10`

# Issues

**Things that could be improved, if we had more time:**

- Data Loading for Dash is not efficient. If multiple users connect to Dash, performance goes down a lot.
