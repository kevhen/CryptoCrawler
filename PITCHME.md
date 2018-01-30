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

Holger


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
@title[Problem with Speed]

## 🗲 Problems
# <span class="pink">