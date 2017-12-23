# Presentation
For the presentation, we can use [GitPitch](https://gitpitch.com/), 
a Markdown Presentation Service, that can be accessed via URL 
https://gitpich.com/$user/$repo/$branch , but we need to set the repo 
public first. I created `PITCHME.md` with a default template for the presentation. 
We could build on that.

# Architecture
* I propose a Microservice Architecture: Stateless Docker Containers, 
which are configured via a config.yaml file.

## Microservice 1: Mongo DB
* Serving as data storage
* DB is persisted on a Docker Volumn

## Microservice 2: Twitter Stream Listener
* Based on Anaconder Docker Image
* Storing the Tweets into Mongo DB

