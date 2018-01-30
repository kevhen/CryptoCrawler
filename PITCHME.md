@title[Title]

# CryptoCrawler

#### Mining information about Crypto-Currencies from the Web.
<br>
<div class="byline">by Holger Büch & Kevin Hendel</div>
<br>
<div class="hdm-module">
Module "Web & Social Media Analytics"<br>
by Prof. Dr. Stephan Wilczek, Prof. Dr. Jan Kirenz<br>
Master Data Sciene & Business Analytics<br>
University of Media Stuttgart, Germany<br>
</div>

---?image=assets/bg-idea.png
@title[Introduction]

#### Introduction
# Idea & Planning


+++
@title[Goal]

#### Goal
- Topic: Ongoing Hype on Crypto-Currencies in 2017 and 2018
- Idea A: Correlate development of Tweets and Stock-Values over time.
- Idea B: Provide additional information, that helps to interpret those developments.
- Idea C: Automatically buy/sell stocks based on prediction. (not done)
- Try and use new technologies
- Gain experience as a reward for the overhead in DevOps


+++
@title[Data Sources]

#### Data Sources
- Twitter Stream
- Crypto-Stock-Market Stream
- Crypto-Prices API
- News (planned)


+++
@title[KPIs]

#### KPIs
- Correlation coefficent between Stock-Values and (Sentiment of) Tweets
- Delay between events in Stock-Values and on Twitter


+++
@title[Setup]
#### Project Setup

**Github** for collaboration
+ Feature Branches & Pull requests
+ Ticketing / Bugs Tracking
+ Slides (gitpitch)

+++
@title[Setup2]

**AWS** for Hosting
+ t2.medium running Ubuntu
+ Access via SSH

+++
@title[Setup3]

**Architecture**
+ Docker based virtualized Microservices


---?image=assets/bg-docker2.png
@title[Architecture]

#### Architecture
# Docker based Microservices


+++
@title[Docker]

#### Docker
- virtualized Containers for each part of the software
- independent from host system
- deployable locally and in the cloud
- brings all dependencies

+++

#### Dockerfile

```yaml
FROM continuumio/miniconda3

RUN conda install -y pymongo pyyaml
RUN conda install -c conda-forge -y tweepy
RUN conda install -c gomss-nowcast schedule

WORKDIR /home
RUN git clone https://github.com/kevhen/CryptoCrawler.git

WORKDIR /home/CryptoCrawler/crypto-price-crawler

CMD while true; do python pricelistener.py; done
```

@[1](Get defined base image online)
@[3,4,5](Install additional packages)
@[8](Clone project into the container)
@[12](Run python script in a loop in case it exits with an error)

+++
@title[Microservices]

#### Microservices
- one Microservice each for single (or small set of) functions
- every Microservice is independent and stateless
- restarting of single services or the system without breaking it
- internal and external networking

+++
@title[Docker Compose]

#### Docker Compose

Configuration file (docker-compos.yaml)

```yaml
version: '3'

networks:
  backend:
    internal: true
  frontend:
    internal: false

services:
  crypto-mongo:
    image: mongo:jessie
    volumes:
      - /data/mongodb:/data/db:rw
    networks:
      - backend
    entrypoint:
      - docker-entrypoint.sh
      - --storageEngine
      - mmapv1

  crypto-jupyter:
    volumes:
      - /data/notebooks:/home/jovyan/work
    networks:
      - backend
      - frontend
    ports:
      - 8888:8888
    build:
      context: ./jupyter
    depends_on:
      - crypto-mongo
    entrypoint:
      - start-notebook.sh
      - --NotebookApp.password='sha1:f6a0093ff7ca:be25a6064ba30e37265b0f800cbb925c636cc4fe'
  .
  .
  .
  .
```

@[1](docker-compose version)

@[3,4,5,6,7](Define virtual networks for the containers)
@[4,5](Internal backend network for the Database. Not accessible from outside the containers)
@[6,7](Hybrid network. Accessible by the containers and from outside via mapped ports)

@[9](Definition of two example microservices)

@[10,11,12,13,14,15,16,17,18,19](MongoDB)
@[11](Base Image)
@[12,13](Connect external volumes)
@[14,15](Define network connection)
@[16,17,18,19](Start script inside the container and additional parameters)

@[21,22,23,24,25,26,27,28,29,30,31,32,33,34,35](Jupyter Notebook)
@[22,23](Connect external volumes)
@[24,25,26](Define network connections)
@[27,28](Map internal to external ports)
@[31,32](Dependencies to specify build and start order)
@[33,34,35](Start script inside the container and additional parameters)


+++
@title[In Action]

#### In Action
- `docker-compose build`
- `docker-compose up`

Combined log output

```shell
twitter-listener_1       | INFO - 01/30/2018 15:32:36: 374000 Tweets received. Still listening...
crypto-price-listener_1  | INFO - 01/30/2018 15:32:36: Prices are {'BTC': {'USD': 10407.7, 'EUR': 8416.89}, 'ETH': {'USD': 1115.7, 'EUR': 907.42}, 'IOT': {'USD': 2.39, 'EUR': 1.95}}
crypto-price-listener_1  | INFO - 01/30/2018 15:32:36: Trying to save the prices for timestamp 1517326356797 to mongo
crypto-price-listener_1  | INFO - 01/30/2018 15:32:36: Saved prices. Waiting until next call
crypto-dash_1            | INFO - 01/30/2018 15:32:38: 37.201.7.172 - - [30/Jan/2018 15:32:38] "POST /_dash-update-component HTTP/1.1" 200 -
crypto-dash_1            | INFO - 01/30/2018 15:32:43: 37.201.7.172 - - [30/Jan/2018 15:32:43] "POST /_dash-update-component HTTP/1.1" 200 -
crypto-price-listener_1  | INFO - 01/30/2018 15:32:46: Running job Every 10 seconds do startListening({'mongodb': {'host': 'crypto-mongo', 'port': 27017, 'db': 'cryptocrawl'}, 'cryptocompare': {'coinlist': 'https://min-api.cryptocompare.com/data/all/coinlist', 'price': 'https://min-api.cryptocompare.com/data/pricemulti'}, 'collections': {'generalcrypto': {'keywords': ['blockchain', 'crypto', 'altcoins', 'altcoin']}, 'bitcoin': {'keywords': ['bitcoin', 'bitcoins'], 'currencycode': 'BTC'}, 'ethereum': {'keywords': ['ethereum'], 'currencycode': 'ETH'}, 'iota': {'keywords': ['iota', 'iotas'], 'currencycode': 'IOT'}, 'trump': {'keywords': ['trump']}, 'car2go': {'keywords': ['car2go']}}, 'dash': {'live': {'default': ['bitcoin', 'ethereum', 'iota'], 'interval': 5}}}, Database(MongoClient(host=['crypto-mongo:27017'], document_class=dict, tz_aware=False, connect=True), 'cryptocrawl')) (last run: 2018-01-30 15:32:36, next run: 2018-01-30 15:32:46)
crypto-price-listener_1  | INFO - 01/30/2018 15:32:46: Starting Currency Listener
crypto-price-listener_1  | INFO - 01/30/2018 15:32:47: Valid coins are ['BTC', 'ETH', 'IOT']
crypto-price-listener_1  | INFO - 01/30/2018 15:32:47: The coin string is BTC,ETH,IOT
crypto-price-listener_1  | INFO - 01/30/2018 15:32:48: Prices are {'BTC': {'USD': 10403.83, 'EUR': 8412.23}, 'ETH': {'USD': 1115.97, 'EUR': 903.88}, 'IOT': {'USD': 2.39, 'EUR': 1.94}}
crypto-price-listener_1  | INFO - 01/30/2018 15:32:48: Trying to save the prices for timestamp 1517326368073 to mongo
crypto-price-listener_1  | INFO - 01/30/2018 15:32:48: Saved prices. Waiting until next call
crypto-dash_1            | INFO - 01/30/2018 15:32:48: 37.201.7.172 - - [30/Jan/2018 15:32:48] "POST /_dash-update-component HTTP/1.1" 200 -
crypto-dash_1            | INFO - 01/30/2018 15:32:53: 37.201.7.172 - - [30/Jan/2018 15:32:53] "POST /_dash-update-component HTTP/1.1" 200 -
```

+++
@title[Centralized Configuration]

#### Centralized Configuration

- one configuration file for changes in a single place

```yaml
mongodb:
    host: crypto-mongo
    port: 27017
    db:   cryptocrawl

cryptocompare:
    coinlist: https://min-api.cryptocompare.com/data/all/coinlist
    price: https://min-api.cryptocompare.com/data/pricemulti
    histo: https://min-api.cryptocompare.com/data/histo

collections:
    generalcrypto:
        keywords:
            - blockchain
            - crypto
            - altcoins
            - altcoin
    bitcoin:
        keywords:
            - bitcoin
            - bitcoins
        currencycode: BTC
    ethereum:
        keywords:
            - ethereum
        currencycode: ETH
    iota:
        keywords:
            - iota
            - iotas
        currencycode: IOT
    trump:
        keywords:
            - trump
    car2go:
        keywords:
            - car2go

dash:
    live:
        default:
            - bitcoin
            - ethereum
            - iota
        interval: 5

```
@[1,2,3,4](MongoDB connection information
@[6,7,8,9](URLs to the CryptoCompare API)
@[11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37](URLs to the CryptoCompare API)
@[39,40,41,42,43,44,45](URLs to the CryptoCompare API)

---?image=assets/bg-mongodb.png
@title[Microservice - MongoDB]

#### Microservice 1
# Mongo DB

Holger


+++
@title[MongoDB]

#### MongoDB
- Document based Database
- A Document contains a JSON object
- Multiple Documents grouped to Collections
- Database can be queried


+++
@title[Problem with Speed]

#### Problem 1
- Slow (CPU-eating) on Queries over Timestamp

#### Solution
- Create Index on Timestamp attribute
- Aggregate in DB, where possible


+++


```shell
$ docker exec -it crypto-mongo /bin/bash
$ mongo
Mongo > use cryptocrawl
Mongo > show collections
> bitcoin
> ethereum
> generalcrypto
> iota
Mongo > db.bitcoin.createIndex({"timestamp_ms": 1}, {background:true})
Mongo > db.collection.totalIndexSize()
```

@[1](Open shell in Docker Container)
@[2](Start MongoDB CLI client)
@[3](Open Database with Name "cryptocrawler")
@[4](List all collections of this DB)
@[9](Create Index on attribute 'timestamp_ms'. Repeat for all collections.)
@[10](Show size of Indexes. Should fit in RAM.)

+++
@title[Problem with Aggregation]

#### Problem 1
- MongoDB can aggregate DateTime-Object on Intervals.
- But we get Timestamps in Milliseconds from Twitter.
- How to aggregate Milliseconds?

#### Solution A
- Create & store DateTime value

#### Solution B
- Use Math


---?image=assets/bg-twitterlistener.png
@title[Twitter Stream Listener]

#### Microservice 2
# Twitter Stream Listener

Holger


+++
@title[Twitter Stream - Information overload]

#### Problem 1: Too much information

Over <span class="pink">500 MB</span> Data during first two hours.

Over <span class="pink">600 Tweets</span> per minute:
![Tweets after two hours](assets/too_much_data.png)


+++
@title[Twitter Stream - Information overload - solution]

#### Solution

Limit Stored attributes
- TweetID
- Text
- Timestamps
- Geo-Information

Limit stored Tweets
- Exclude everything not EN
- Exclude Retweets


+++
@title[Twitter Stream - Bug]

#### Problem 2: Bug in Tweepy Module
```
File "tstreamer.py", line 109, in
myStream.userstream("with=following")
File "/mnt/d5ddf659-feb7-4daf-95c6-09797c84aa98/venvs/python2ds/lib/python2.7/site-packages/tweepy/streaming.py", line 394, in userstream
self._start(async)
File "/mnt/d5ddf659-feb7-4daf-95c6-09797c84aa98/venvs/python2ds/lib/python2.7/site-packages/tweepy/streaming.py", line 361, in _start
self._run()
File "/mnt/d5ddf659-feb7-4daf-95c6-09797c84aa98/venvs/python2ds/lib/python2.7/site-packages/tweepy/streaming.py", line 294, in _run
raise exception
AttributeError: 'NoneType' object has no attribute 'strip'
```
https://github.com/tweepy/tweepy/issues/869 (open since March 2017)


+++
@title[Twitter Stream - Bug - Solution]

#### Solution A
Tried older Version: `conda install -c conda-forge -y tweepy=3.2.0`
Didn't work.

#### Solution B
**Workaround:**
- Handle Exceptions and reconnect Tweepy:
`bla bla`
- Just in case: Auto-restart Microservice on exit:
`while true; do python streamlistener.py; done`


---?image=assets/bg-pricecrawler.png
@title[Microservice - Price Crawler]

#### Microservice 3
# Crypto Price Crawler

+++

#### Crypto Price Crawler

- receive prices in a defined interval
- call api to get all currencies and their current values
- save the values to the database each in a separate collection

+++

#### Scheduled listener

```python
def init():
    with open('../config.yaml', 'r') as stream:
        conf = yaml.load(stream)
    # Open a connection to mongo:
    client = MongoClient(conf['mongodb']['host'], conf['mongodb']['port'])
    db = client[conf['mongodb']['db']]
    schedule.every(10).seconds.do(startListening, conf, db)
```

@[2,3](Load config file)
@[5,6](Connect to the database)
@[7](Schedule listener to run every 10 seconds)

+++

#### REST API Call

```python
def getPricesOnce(currencies, conf):
    """Gets the current price for the currencies defined in the config.yaml"""
    payload = { 'fsyms': currencies, 'tsyms': 'USD,EUR' }
    response = requests.get(conf['cryptocompare']['price'], params=payload)
    if response.status_code == 200:
        prices = json.loads(response.content)
        logger.info('Prices are {}'.format(prices))
        return prices
    else:
        logger.warn('Could not get prices. Error code {}'.format(response.status_code))
        return False
```

@[1](Crypto `currencies` as a comma-separated string and `conf` (config) as parameters)
@[3](Build payload for the REST-Call)
@[4](Send request and save response)
@[5,6,7,8](Handle successful request and parse content)
@[9,10,11](Handle error case)


---?image=assets/bg-cryptowrapper.png
@title[Microservice - API Wrapper]

#### Microservice 4
# Crypto API Wrapper

+++

#### Crypto API Wrapper

- serve an API as an interface between the dashboard and the database or external APIs

- benefits
  - prevent direct database access
  - filter data and fit format for later needs
  - less logic in the frontend

- using `Flask` framework to build the actual API

+++

#### Random tweets endpoint

- return random tweets about certain topics in a defined timeframe

Example: `/tweets?topics=bitcoin,ethereum,iota&amount=5&from=1516110498&to=1516290284`

```python
def getTweetsForTopics(topicstring, amount, fromTs, toTs):
    topicList = parseTopics(topicstring)
    randomTweets = []
    for topic in topicList:
        cursor = db[topic].aggregate([
                { '$match': { 'timestamp_ms': {'$gt': fromTs , '$lt': toTs }}},
                { '$sample': { 'size': amount } },
                { '$project' : { '_id': 0 } }
            ])
        tweetListForTopic = list(cursor)
        identifiedTweetListForTopic = []
        for singleTweet in tweetListForTopic:
            identifiedTweet = { 'topic': topic, 'tweet': singleTweet }
            identifiedTweetListForTopic.append(identifiedTweet)
        randomTweets = randomTweets + identifiedTweetListForTopic
    if len(randomTweets) >= amount:
        randomListFinal = random.sample(randomTweets, amount)
    else:
        randomListFinal = randomTweets
    resultDict = {'tweets': randomListFinal }
    return resultDict
```

@[1](Get URL parameters as input)
@[2](Get list of topics from the comma separated `topicstring`)
@[4](Do one request for each topic because every topic is in a separate mongo collection)
@[5,6,7,8,9](Build mongo aggregation)
@[6](Match all entries between the start and the end timestamps)
@[7](Get a random sample with the specified size from the matched entries
@[8](Remove the `_id` information from the results)
@[12,13,14](Add the topic to each tweet)
@[17](From all sample tweets from the collections we take a sample as big as the specified amount)

+++

#### Add endpoint in Flask

```python
class RandomTweets(Resource):
    def get(self):
        now = int(time.time())

        fromTs = handleTs(request.args.get('from'), now) * 1000
        toTs = handleTs(request.args.get('to'), now) * 1000

        topicstring = request.args.get('topics')
        amount = parseAmount(request.args.get('amount'))

        result = getTweetsForTopics(topicstring, amount, fromTs, toTs)
        return jsonify(result)

api.add_resource(RandomTweets, '/tweets')
```

@[3](Get current timestamp for timeframe calculations)
@[5](Handle the begin of the timeframe. Check that it is not in the future. Calculate milliseconds from seconds)
@[6](Handle the end of the timeframe. Check that it is not in the future. Calculate milliseconds from seconds. Set now as default if not set.)
@[8](Get the passed topicstring)
@[9](Handle the amount)
@[11](Do the actual request with all parameters)
@[12](Return the result as a json)
@[14](Add the endpoint to Flask at the route `/tweets`)

+++

#### Additional historical price endpoint

- endpoint to retrieve historical prices from the CryptoCompare API
- implemented to take a timeframe and parse the parameters to fit the CryptoCompare API definitions
- returns the daily, hourly or minutely prices for a crypto currency
- planned to replace or support the price listener or replace missing values from system outages
- not yet integrated into the dashboard

---?image=assets/bg-anomaly.png
@title[Microservice - Anomaly Detection]

#### Microservice 5
# Anomaly Detection

Holger


+++
@title[Idea]

#### Idea
Detect 'unusual' Events in:
- Amount of Tweets received
- Amount of Tweets with pos/neg sentiment
- Prices of Crypto-Currencies
Then use them for:
- Visualization in Dashboard
- Searching News in those time ranges
to <span class="pink">ease the interpretation</span> of the data.


+++
@title[Anomalies in Timeseries]


<br>
#### Create slideshow content using GitHub Flavored Markdown in your
favorite editor.

<span class="aside">It's as easy as README.md with simple
slide-delimeters (---)</span>


---?image=assets/bg-topic.png
@title[Microservice - Topic Modelling]

#### Microservice 6
# Topic Modelling

Holger


+++
@title[Step 2. Git-Commit]

### <span class="gold">STEP 2. GIT-COMMIT</span>
<br>

```shell
$ git add PITCHME.md
$ git commit -m "New slideshow content."
$ git push

Done!
```

@[1](Add your PITCHME.md slideshow content file.)
@[2](Commit PITCHME.md to your local repo.)
@[3](Push PITCHME.md to your public repo and you're done!)
@[5](Supports GitHub, GitLab, Bitbucket, GitBucket, Gitea, and Gogs.)


---?image=assets/bg-jupyter.png
@title[Microservice - Jupyter Notebook]

#### Microservice 7
# Jupyter Notebook

+++

#### Integrate an instance of Jupyter notebook

- Jupyter notebook inside of an own container
- connection to the database and all other services
- test environment for database and API calls
- fast response without redeploying of any of the components

---?image=assets/bg-dash.png
@title[Microservice - Dash]

#### Microservice 8
# Dashbord

+++

#### Show random tweets from the selected timeframe


---
@title[Wrap up]

#### What we have learned
# Wrap up
