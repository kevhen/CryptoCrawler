@title[Title Slide]

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


---
@title[Markdown Syntax Demo]

# Headline 1
## Headline 2
### Headline 3
#### Headline 4
##### Headline 5

Text <span class="pink">with pink</span> and **bold**, *italic* and normal words and a [Link](https://github.com).

- Numeration A
- Numeration B
    - Sub Numeration A
    - Sub Numeration B


+++
@title[Markdown Syntax Demo]

### Source Code

Some Code Examples:

`Single Code line`

```python
if self.mute is not True:
    logger.info('Receiving tweets...')
    self.mute = True
```

+++
@title[Markdown Syntax Demo]

### Color Scheme for Background
- #2779CC
- #D66216
- #CCA91F
- #00A91F

RecursionError
```
crypto-price-listener_1  |     self._backend, self._x509
crypto-price-listener_1  |   File "/opt/conda/lib/python3.6/site-packages/cryptography/hazmat/backends/openssl/decode_asn1.py", line 249, in parse
crypto-price-listener_1  |     value = handler(backend, ext_data)
crypto-price-listener_1  |   File "/opt/conda/lib/python3.6/site-packages/cryptography/hazmat/backends/openssl/decode_asn1.py", line 428, in _decode_subject_alt_name
crypto-price-listener_1  |     _decode_general_names_extension(backend, ext)
crypto-price-listener_1  |   File "/opt/conda/lib/python3.6/site-packages/cryptography/x509/extensions.py", line 1008, in __init__
crypto-price-listener_1  |     self._general_names = GeneralNames(general_names)
crypto-price-listener_1  |   File "/opt/conda/lib/python3.6/site-packages/cryptography/x509/extensions.py", line 964, in __init__
crypto-price-listener_1  |     if not all(isinstance(x, GeneralName) for x in general_names):
crypto-price-listener_1  |   File "/opt/conda/lib/python3.6/site-packages/cryptography/x509/extensions.py", line 964, in <genexpr>
crypto-price-listener_1  |     if not all(isinstance(x, GeneralName) for x in general_names):
crypto-price-listener_1  |   File "/opt/conda/lib/python3.6/abc.py", line 182, in __instancecheck__
crypto-price-listener_1  |     if subclass in cls._abc_cache:
crypto-price-listener_1  |   File "/opt/conda/lib/python3.6/_weakrefset.py", line 72, in __contains__
crypto-price-listener_1  |     wr = ref(item)
crypto-price-listener_1  | RecursionError: maximum recursion depth exceeded while calling a Python object
```


---
@title[Introduction]

#### Introduction
# Idea & Planning

Kevin


+++
@title[Goal]

#### Goal
- Topic: Hype on Crypto-Currencies
- Idea A: Correlate development of Tweets and Stock-Values over time.
- Idea B: Provide additional information, that helps to interpret those developments.
- Idea C: Automatically buy/sell stocks based on prediction. (not done)


+++
@title[Data Sources]

#### Data Sources
- Twitter Stream
- Crypto-Stock-Market Stream
- News


+++
@title[KPIs]

#### KPIs
- Correlation coefficent between Stock-Values and (Sentiment of) Tweets
- Delay between events in Stock-Values and on Twitter


+++
@title[Setup]
#### Project Setup
**Github** for collaboration
- Feature Branches & Pull requests
- Ticketing / Bugs Tracking
- Slides (gitpitch)

**AWS** for Hosting
- t2.medium running Ubuntu
- Access via SSH

**Architecture**
- Docker based Microservices


---
@title[Architecture]

#### Architecture
# Docker based Microservices

Kevin


+++
@title[Docker]

#### Docker
- Virtualized Containers for each Microservice
-

+++
@title[Microservices]

#### Microservices
- to do (stateless, independent,...)


+++
@title[In Action]

#### In Action
- to do (Build, Run, Docker-Compose)


---?image=assets/bg-mongodb.png
@title[Microservice - MongoDB]

#### Microservice 1
# Mongo DB


+++
@title[MongoDB]

#### MongoDB
- Document based Database
- A Document contains a JSON object
- Multiple Documents grouped to Collections
- Documents can be queried using JSON-based Syntax


+++
@title[Store Documents]

#### Storing Documents with Python

```query
from pymongo import MongoClient

client = MongoClient('crypto-mongo', 27017)
db = client['cryptocrawl']

json_obj = {
    'timestamp_ms': 1517343098,
    'text': 'Something...'
    }

db['bitcoin'].insert(json_obj)
```
@[1](Import Module (has to be installed))
@[3](Initialize Client-Connection to MongoDB)
@[4](Select Database)
@[6-9](MongoDB ♥ JSON Documents)
@[11](Write JSON as Document in a Collection)


+++
@title[Query Documents]

#### Query Documents with Python

```python
import pandas
from pymongo import MongoClient

client = MongoClient('crypto-mongo', 27017)
db = client['cryptocrawl']

query = {'timestamp_ms': {'$gt': 1517343098}}
projection = {'text': 1, 'timestamp_ms': 1}

cursor = db['bitcoin'].find(query, projection).limit(100)

df = pandas.DataFrame(list(cursor))
```
@[1-5](Import Module, Initialize Client-Connection to MongoDB)
@[7](Define Filter (similar to WHERE in SQL))
@[8](Define Fields to return (similar to SELECT in SQL))
@[10](find() returns a cursor object (here also limited to 100 results))
@[12](Cursor can be converted into list and transformed into Pandas Dataframe)

<p class="fragment pink center">
*Show in Robo RT*
</p>


+++
@title[Problems]

## Problems
# <span class="pink">⚔</span>


+++
@title[Problem with Speed - 1]

#### <span class="pink">⚔</span> Slow Queries over Timestamp
- We often query for a specified range in the timestamp, e.g:
```python
query = {'timestamp_ms': {'$gt': 1517243098, '$lt': 1517343098}}
```
- Performance was weak
- CPU usage on VM peaked


+++
@title[Problem with Speed - 2]

#### <span class="pink">✓</span> Create Index on Timestamp attribute

```shell
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

@[1](Start MongoDB CLI client)
@[2](Open Database with Name "cryptocrawler")
@[3-7](List all collections of this DB)
@[8](Create Index on attribute 'timestamp_ms'. Repeat for all collections.)
@[9](Show size of Indexes. Should fit in RAM.)
@[0-9]()

+++
@title[Problem with Aggregation - 1]

#### <span class="pink">⚔</span> Aggregate by Timestamp in Milliseconds
- We need to aggregate on Time-Intervals, e.g. for Tweets per Hour
- MongoDB can aggregate DateTime-Object on Intervals
- But we get Timestamps in Milliseconds from Twitter
- How to aggregate Integer with Milliseconds per hours?

+++
@title[Problem with Aggregation - 2]

#### <span class="pink">✓</span> Aggregate using Math
- To aggregate Milliseconds by Hours, get Milliseconds per hour: |
```
1 Hour is 1000ms * 60sec * 60min = 3.600.000 ms
```
- Then divide Timestamp by this value and round to floor: |
```
floor (timestamp / 3.600.000)
```
- All timestamps from the same hour will result in the same value |
- Then Aggregation can be done on this value |
- Sadly, MongoDB has no floor Function |
- Luckily, it has a modulo Function: |
```
timestamp/3.600.000 – ( (timestamp/3.600.000) mod 1)
```

+++
@title[Problem with Aggregation - 3]

#### <span class="pink">✓</span> Alternative Solutions
- Cast to DateTime during Query
- Convert & store Milliseconds as DateTime value

*Would those be faster?*


---?image=assets/bg-twitterlistener.png
@title[Twitter Stream Listener]

#### Microservice 2
# Twitter Stream Listener

Holger

+++
@title[Tweepy]

#### Using Tweepy to listen to Twitter Streaming API

```python
import tweepy

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status.text)  # Then store the tweets...
    def on_error(self, status_code):
        if status_code == 420:
            time.sleep(300) # Then reconnect ...

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

stream_listener = MyStreamListener(conf=conf)
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(track=list(['bitcoin','iota','...']), async=True)
```
@[1](Import Module)
@[3](Inherit StreamListener class)
@[4-5](Define what to do if tweet arrives)
@[6-8](Handle API Error, especially 420 to avoid penalty)
@[10-13](Set credentials and create API object)
@[15-18](Instanciate class, start listening to Tweets with keywords)
@[0-18]()


+++
@title[Problems]

## Problems
# <span class="pink">⚔</span>


+++
@title[Information overload - 1]

#### <span class="pink">⚔</span> Too much information

- Over <span class="pink">500 MB</span> Data during first two hours.
- Over <span class="pink">900 Tweets</span> per minute

![Tweets after two hours](assets/too_much_data.png)
*Tweets per 15min, only crypto topics*

+++
@title[Information overload - 1]

#### <span class="pink">✓</span> Limit Tweets
- Exclude everything not EN |
- Exclude Retweets |

#### <span class="pink">✓</span> Limit Stored attributes |
- TweetID |
- AuthorID
- Text
- Timestamps
- Geo-Information




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

Kevin


---?image=assets/bg-cryptowrapper.png
@title[Microservice - API Wrapper]

#### Microservice 4
# Crypto API Wrapper

Kevin


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

Kevin


---?image=assets/bg-dash.png
@title[Microservice - Dash]

#### Microservice 8
# Dashbord

Holger & Kevin


+++
@title[Step 3. Done!]

### <span class="gold">STEP 3. GET THE WORD OUT!</span>
<br>
![GitPitch Slideshow URLs](assets/images/gp-slideshow-urls.png)
<br>
<br>
#### Instantly use your GitPitch slideshow URL to promote, pitch or
present absolutely anything.


---
@title[Wrap up]

#### What we have learned
# Wrap up
