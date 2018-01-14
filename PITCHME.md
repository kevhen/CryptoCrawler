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

![Tweets after two hours](assets/too_much_data.png)

---?image=assets/bg-twitterlistener.png
@title[Twitter Stream Listener]

#### Microservice 2
# Twitter Stream Listener

+++

@title[Twitter Stream - Information overload]

#### Problem 1: Too much information

Over <span class="pink">500 MB</span> Data during first two hours.

Over <span class="pink">6000 Tweets</span> every ten minutes:
![Tweets after two hours](assets/too_much_data.png)

+++

@title[Twitter Stream - Information overload - solution]

#### Solution

Limit Stored attributes

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

#### Problem 2: Bug in Tweepy Module
Try older Version: `conda install -c conda-forge -y tweepy=3.2.0`
Didn't work.
Workaround:
Auto-restart on exit:
`while true; do python streamlistener.py; done`

---

#### No more <span class="gray">Keynote</span>.
#### No more <span class="gray">Powerpoint</span>.
<br>
#### Just <span class="gold">Markdown</span>.
#### Then <span class="gold">Git-Commit</span>.

---?code=assets/md/hello.md&title=Step 1. PITCHME.md

<br>
#### Create slideshow content using GitHub Flavored Markdown in your
favorite editor.

<span class="aside">It's as easy as README.md with simple
slide-delimeters (---)</span>

---

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

---

@title[Step 3. Done!]

### <span class="gold">STEP 3. GET THE WORD OUT!</span>
<br>
![GitPitch Slideshow URLs](assets/images/gp-slideshow-urls.png)
<br>
<br>
#### Instantly use your GitPitch slideshow URL to promote, pitch or
present absolutely anything.

---

@title[Slide Rich]

### <span class="gold">Slide Rich</span>

#### Code Presenting for Blocks, Files, and GISTs
#### Image, Video, Chart, and Math Slides
#### Multiple Themes with Easy Customization
<br>
#### <span class="gold">Plus collaboration is built-in...</span>
#### Your Slideshow is Part of Your Project
#### Under Git Version Control within Your Git Repo

---

@title[Feature Rich]

### <span class="gold">Feature Rich</span>

#### Present Online or Offline
#### With Speaker Notes Support
#### Print Presentation as PDF
#### Auto-Generated Table-of-Contents
#### Share Presentation on Twitter or LinkedIn

---

### <span class="gold">GitPitch Pro - Coming Soon!</span>

<br>
<div class="left">
    <i class="fa fa-user-secret fa-5x" aria-hidden="true"> </i><br>
    <a href="https://gitpitch.com/pro-features" class="pro-link">
    More details here.</a>
</div>
<div class="right">
    <ul>
        <li>Private Repos</li>
        <li>Private URLs</li>
        <li>Password-Protection</li>
        <li>Image Opacity</li>
        <li>SVG Image Support</li>
    </ul>
</div>

---

### Go for it.
### Just add <span class="gold">PITCHME.md</span> ;)
