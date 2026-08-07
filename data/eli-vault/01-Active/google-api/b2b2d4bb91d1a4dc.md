---
id: b2b2d4bb91d1a4dc
source: "google-workspace-api-tools.md"
"title: Google Workspace & Productivity API Tools"
category: google-api
skillTags: ["tool", "code"]
containmentHash: 65e2ea5075c83167e5a0
createdAt: 1786051356911
embeddingSig: "client:sudo:pip3|google:python:client|install:google:python|install:oauth2client:will|need:nltk:downloader|nltk:downloader:obtain|oauth2client:will:need|pip3:install:google|pip3:install:oauth2client|python:client:sudo|sudo:pip3:install|will:need:nltk"
---
sudo pip3 install google-api-python-client==1.7.8
$ sudo pip3 install oauth2client==4.1.3
```
You will need to use the NLTK Downloader to obtain punkt:

```
$ python3
>>> import nltk
>>> nltk.download("punkt")
>>> exit()
```
### Download this repository:

```
$ git clone https://github.com/crhenr/youtube-video-maker.git
```
### Add your API keys