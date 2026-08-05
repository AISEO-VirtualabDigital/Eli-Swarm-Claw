# Google Workspace & Productivity API Tools

Tools and libraries for interacting with Google Workspace services: Drive, Gmail, Calendar, Sheets, Docs, Chat, Admin, Photos, YouTube, Contacts, Meet, Places, and Tag Manager.

## googleworkspace/cli ⭐30,215

**URL**: https://github.com/googleworkspace/cli

**Description**: Google Workspace CLI — one command-line tool for Drive, Gmail, Calendar, Sheets, Docs, Chat, Admin, and more. Dynamically built from Google Discovery Service. Includes AI agent skills.

<h1 align="center">gws</h1>

**One CLI for all of Google Workspace — built for humans and AI agents.**<br>
Drive, Gmail, Calendar, and every Workspace API. Zero boilerplate. Structured JSON output. 40+ agent skills included.

> [!NOTE]
> This is **not** an officially supported Google product.

<p>
  <a href="https://www.npmjs.com/package/@googleworkspace/cli"></a>
  <a href="https://github.com/googleworkspace/cli/blob/main/LICENSE"></a>
  <a href="https://github.com/googleworkspace/cli/actions/workflows/ci.yml"></a>
  <a href="https://www.npmjs.com/package/@googleworkspace/cli"></a>
</p>
<br>

⬇️ **[Download the latest release for your OS](https://github.com/googleworkspace/cli/releases)**

`gws` doesn't ship a static list of commands. It reads Google's own [Discovery Service](https://developers.google.com/discovery) at runtime and builds its entire command surface dynamically. When Google Workspace adds an API endpoint or method, `gws` picks it up automatically.

> [!IMPORTANT]
> This project is under active development. Expect breaking changes as we march toward v1.0.

## Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Why gws?](#why-gws)
- [Authentication](#authentication)
- [AI Agent Skills](#ai-agent-skills)
- [Advanced Usage](#advanced-usage)
- [Environment Variables](#environment-variables)
- [Exit Codes](#exit-codes)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Prerequisites

- **Node.js 18+** — for `npm install` (or download a pre-built binary from [GitHub Releases](https://github.com/googleworkspace/cli/releases))
- **A Google Cloud project** — required for OAuth credentials. You can create one via the [Google Cloud Console](https://console.cloud.google.com/) or with the [`gcloud` CLI](https://cloud.google.com/sdk/docs/install) or with the `gws auth setup` command.
- **A Google account** with access to Google Workspace

## Installation

The recommended way to install `gws` is to download the pre-built binary for your OS and architecture from the **[GitHub Releases](https://github.com/googleworkspace/cli/releases)** page. Extract the archive and place the `gws` binary in your `$PATH`.

For convenience, you can also use `npm` to automate downloading the appropriate binary from GitHub Releases:

```bash
npm install -g @googleworkspace/cli
```

Or build from source:

```bash
cargo install --git https://github.com/googleworkspace/cli --locked
```

A Nix flake is also available at `github:googleworkspace/cli`

```bash
nix run github:googleworkspace/cli
```

On macOS and Linux, you can also install via [Homebrew](https://brew.sh/):

```bash
brew install googleworkspace-cli
```

## Quick Start

```bash
gws auth setup     # walks you through Google Cloud project config
gws auth login     # subsequent OAuth login
gws drive files list --params '{"pageSize": 5}'
```

## Why gws?

**For humans** — stop writing `curl` calls against 

---

## GAM-team/GAM ⭐4,255

**URL**: https://github.com/GAM-team/GAM

**Description**: command line management for Google Workspace

GAM is a command line tool for Google Workspace admins to manage domain and user settings quickly and easily.

# Quick Start

## Linux / MacOS

Open a terminal and run:

```sh
bash <(curl -s -S -L https://gam-shortn.appspot.com/gam-install)
```

this will download GAM, install it and start setup.

## Windows

Download the EXE Installer from the [GitHub Releases] page. Run it and you'll be prompted to setup GAM.

## Use your own Python
If you'd prefer to install GAM as a Python package you can install with pip:
```
pip install gam7
```
# Documentation

The GAM documentation is hosted in the [GitHub Wiki]

# Mailing List / Discussion group

The GAM mailing list / discussion group is hosted on [Google Groups].  You can join the list and interact via email, or just post from the web itself.

# Chat Room

There is a public chat room hosted in Google Chat. [Instructions to join](https://github.com/GAM-team/GAM/wiki/GAM-Public-Chat-Room).

# Author

GAM is maintained by [Jay (James) Lee](mailto:jay0lee@gmail.com) and [Ross Scroggs](mailto:ross.scroggs@gmail.com). Please direct "how do I?" questions to [Google Groups].

[GAM release]: https://github.com/GAM-team/GAM/releases
[GitHub Releases]: https://github.com/GAM-team/GAM/releases
[GitHub]: https://github.com/GAM-team/GAM/tree/master
[GitHub Wiki]: https://github.com/GAM-team/GAM/wiki/
[Google Groups]: http://groups.google.com/group/google-apps-manager

---

## kiwiz/gkeepapi ⭐1,762

**URL**: https://github.com/kiwiz/gkeepapi

**Description**: An unofficial client for the Google Keep API.

gkeepapi
========

## NOTICE: Google offers an official [API](https://developers.google.com/keep/api) which might be an option if you have an Enterprise account. 🎉

An unofficial client for the [Google Keep](https://keep.google.com) API.

```python
import gkeepapi

# Obtain a master token for your account (see docs)
master_token = '...'

keep = gkeepapi.Keep()
success = keep.authenticate('user@gmail.com', master_token)

note = keep.createNote('Todo', 'Eat breakfast')
note.pinned = True
note.color = gkeepapi.node.ColorValue.Red
keep.sync()
```

*gkeepapi is not supported nor endorsed by Google.*

The code is pretty stable at this point, but you should always make backups. The project is under development, so feel free to open an issue if you have questions, see any bugs or have a feature request. PRs are welcome too!

## Installation

```
pip install gkeepapi
```

## Documentation

The docs are available on [Read the Docs](https://gkeepapi.readthedocs.io/en/latest/).

## Todo (Open an issue if you'd like to help!)

- Reminders
    - `reminders`
- Figure out all possible values for `TaskAssist._suggest` (Same as CategoryValue?)
- Figure out all possible values for `NodeImage._extraction_status` (integer)
- Blobs (Drawings/Images/Recordings)

---

## alyssaxuu/figma-to-google-slides ⭐570

**URL**: https://github.com/alyssaxuu/figma-to-google-slides

**Description**: Convert Figma frames into a Google Slides presentation 🍭

# Figma to Google Slides
![Demo](https://media.giphy.com/media/ZcRFEQw8RjOkDu8QiA/giphy.gif)
<br>
Convert [Figma](https://figma.com) frames into a Google Slides presentation, as showcased [here](https://twitter.com/alyssaxuu/status/1086934646959558656) 📽️

The order of the slides is determined by the frame hierarchy in Figma, from top to bottom in the Chrome Extension, but reversed in the Minified Version.

Made by [Alyssa X](https://alyssax.com)


# Installation (for the Minified Version)

 1. Import the [Google API PHP Library](https://github.com/googleapis/google-api-php-client)! ✨ If you import it without composer, make sure that the path on the first line matches where the library is hosted in your server. Otherwise, you can replace that line from the code.
 2. Create a service API key in the [Google API Console](https://console.cloud.google.com/apis/). You can follow the same steps described in the second section [of my guide on using the Google Sheets API](https://medium.com/hackerpreneur-magazine/how-to-use-google-sheets-as-a-cms-or-a-database-f9d8e736fdce) 📖 . Import it to your server and replace the path in the code.
 3. Go to your Google Slides presentation, click on "Share" and enter the previously generated email address (your service API email address) into the "People" field with edit permissions 🔑
 4. Replace the Google Slides presentation ID and Figma file ID from the code 🔗
 5. Find your personal Figma access token by going to the [API documentation](https://www.figma.com/developers/docs) 🤖, scrolling down to the "Access Tokens" section, and clicking on "Get personal access token" on the right. Replace it in the code.
 6. Run the script & enjoy! Every time you run the script you will update the slides with the different frames from Figma 🍭

# Installation (for the Chrome Extension)

1. Create a Chrome extension with the files in the Chrome Extension folder (you can follow [this guide](https://support.google.com/chrome/a/answer/2714278?hl=en)) 📖
2. Generate a OAuth 2.0 client ID in the [Google API Console](https://console.cloud.google.com/apis/). Select "Chrome App", and insert your App ID (which is generated when you create the extension).
3. In the manifest.json, replace "google_client_id" with your previously generated OAuth 2.0 client ID.
4. Generate an API key, leave it as unrestricted, and replace "google_api_key" in the background.js with the generated API key 🔑
5. Install the extension in your browser and enjoy! 
#
 Feel free to reach out to me through email at hi@alyssax.com or [on Twitter](https://twitter.com/alyssaxuu) if you have any questions or feedback! Hope you find this useful 💜

---

## tanaikech/taking-advantage-of-google-apps-script ⭐446

**URL**: https://github.com/tanaikech/taking-advantage-of-google-apps-script

**Description**: Here, CLI tools, libraries, Add-ons, Reports, Benchmarks and Sample Scripts for taking advantage of Google Apps Script which are publishing in my blog, Gists and GitHub are summarized.

# Taking Advantage of Google Apps Script (Tanaike's list)

<a name="top"></a>
Here, CLI tools, libraries, Reports, Benchmarks and Sample Scripts for taking advantage of Google Apps Script which are publishing in my [blog](https://tanaikech.github.io/), [Gists](https://gist.github.com/tanaikech), [GitHub](https://github.com/tanaikech) and [my answers on Stackoverflow](https://stackoverflow.com/users/7108653/tanaike?tab=answers) are summarized. I hope that you have the chance for knowing the possibilities of Google Apps Script from my contents. If these are useful for you, I'm glad.

Japanese version of this list is [here](https://github.com/tanaikech/taking-advantage-of-google-apps-script/blob/master/Japanese_version/README.md).

<br>

# Index

- [News](#news)
- [Papers](#papers)
- [Trend of Google Apps Script](#trend)
- [Settings](#settings)
- [CLI tools for GAS](#clitool)
- [Gemini CLI Extensions](#geminicliextensions)
- [Web Applications](#webapps)
- [GAS libraries](#gaslibraries)
- [GAS library database](#gaslibrarydatabase)
- [Go libraries](#golibraries)
- [Node.js modules](#nodemodules)
- [Python library](#pythonlibrary)
- [Javascript library](#javascriptlibrary)
- [Add-ons](#addons)
- [Reports](#reports)
- [Benchmarks](#benchmarks)
- [Communities](#communities)
- [Sample Scripts](#samplescripts)
  - [Files in Google Drive](#filesingoogledrive)
  - [Projects](#projects)
  - [Spreadsheets](#spreadsheets)
  - [Documents](#documents)
  - [Slides](#slides)
  - [Gmail](#gmail)
  - [Calendar](#calendar)
  - [Form](#form)
  - [YouTube](#youtube)
  - [Chart](#chart)
  - [Analytics](#analytics)
  - [Slack](#slack)
  - [Virtual Currency](#virtualcurrency)
  - [Stackoverflow](#stackoverflow)
  - [Netatmo](#netatmo)
  - [Figma](#figma)
  - [Microsoft](#microsoft)
  - [Etc](#etc)
  - [Node.js](#nodejs)
  - [Golang](#golang)
  - [Python](#python)
  - [Curl](#curl)
  - [Javascript](#javascript)
  - [PHP](#php)
  - [Generative AI](#generativeai)
  - [Model Context Protocol (MCP)](#mcp)
  - [Agent2Agent Protocol (A2A)](#a2a)
  - [Gemini CLI](#geminicli)
  - [Antigravity](#antigravity)
  - [A2UI: Agent-to-User Interface](#a2ui)

<br>
<br>

<a name="news"></a>

# News

- **September 26, 2025:** [Recipient of the Outstanding Google Developer Expert Award](https://tanaikech.github.io/2025/10/12/recipient-of-the-outstanding-google-developer-expert-award/)
- **June 3, 2024:** [My post was featured in The overwhelmed person’s guide to Google Cloud: week of May 23](https://tanaikech.github.io/2024/06/03/my-post-was-featured-in-the-overwhelmed-persons-guide-to-google-cloud-week-of-may-23/)
- **December 13, 2023:** [Drive API v3 has been released to Advanced Google services](https://tanaikech.github.io/2023/12/13/drive-api-v3-has-been-released-to-advanced-google-services/)
- **August 12, 2023:** [My report has been featured in Google Workspace Developer Newsletter on July 2023](https://tanaikech.git

---

## guyzyl/whatsapp-contact-sync ⭐302

**URL**: https://github.com/guyzyl/whatsapp-contact-sync

**Description**: Easy way to sync between the contact photos on WhatsApp to Google Contacts

# WhatsApp Contact Sync

<p align="center">
    
</p>

<p align="center">
    <a href="https://www.buymeacoffee.com/guyzyl">
        
    </a>
</p>

A simple web app for syncing the profile pictures from WhatsApp to Google Contacts.\
The app matches contacts based on their phone numbers, and utilizes
[whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js) and [Google People API](https://developers.google.com/people) to update the profile picture in Google Contacts.

## Demo

<p align="center">
    
</p>

## Why Was This Developed?

Whenever someone used to call me or I looked them up in my contacts, they all apear as colorful circles with a single letter in it.\
The annoying part is that every single person I know has a WhatsApp account which has a profile picture. They are both based on the same phone number but the picture is only available in one of them.\
In order to fix this grievence I developed this app which allows anyone to sync their contacts photos from WhatsApp to Google Contacts.

## How To Use

The app is extremley easy to use (and self explantory):

1. Go to [whasync.com](https://whasync.com/)
2. Press "Get Started"
3. Scan the QR code with WhatsApp to authorize it
4. Connect you Google account
5. Choose you sync options
6. That's it :)

The whole process is very simple and automated, so you don't need to worry about anything else.\
Setting up should take less then a minute, and syncing should take about 1 second per photo (due to Google's API rate limitiations of 60 requests per user per minute)

## How to Run Locally

In order for the backend to function, it requires an OAuth 2.0 client ID and secret.\
Since (for obvious reasons) this is a private app, you will need to create one for your own.\
You can see instructions on how to do that [here](https://developers.google.com/workspace/guides/create-credentials).\
Once you do that, create the file `server/.env`, and set the following environment variables:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

You also need to add the following **Authorized Redirect URI** to your OAuth 2.0 client in the [Google Cloud Console](https://console.cloud.google.com) based on how you are running the app:

EXAMPLES:
- Local dev: `http://localhost:8080/api/google_callback`
- Docker (port 80): `http://localhost/api/google_callback`
- Production: `https://<your-domain>/api/google_callback`

Once that's done, you can go ahead and run the app:

```bash
# Run backend
cd server
npm install
npm run dev

# Run web app
cd web
npm install
npm run dev
```

## Build Docker Images

There are 3 different `Dockerfile`s for this app:

- [`Dockerfile`](Dockerfile) - This is an image containing both the backend and the web app
- [`Dockerfile`](web/Dockerfile) - An image containing only the web app
- [`Dockerfile`](server/Dockerfile) - An image containing only the backend

In order to build and run the complete app, you need to run the following commands:

```bash
docker build -t whasync .
docker run --rm -i

---

## levz0r/gmail-tester ⭐283

**URL**: https://github.com/levz0r/gmail-tester

**Description**: A simple Node.js Gmail client which checks the inbox for message existence

<p align="center"></p>

# gmail-tester

<span align="center">


<span class="badge-npmdownloads"><a href="https://npmjs.org/package/badges" title="View this project on NPM"></a></span>

![GitHub stars](https://img.shields.io/github/stars/levz0r/gmail-tester?style=social)

</span>

A simple Node.js Gmail client which checks/returns email message(s) straight from any Gmail-powered account (both private and company).<br/>
There are two main functionalities this library provides:<br>

1.  `check_inbox()`: Polls a mailbox for a given amount of time. At the end of the operation, the desired message is returned (if found).
2.  `get_messages()`: Can be used to perform various assertions on the email objects (see example [below](https://github.com/levz0r/gmail-tester/blob/master/README.md#using-get_messages-to-assert-email-body-using-cypress)).

P.S, I have written a [story](https://medium.com/@levz0r/how-to-poll-a-gmail-inbox-in-cypress-io-a4286cfdb888) on medium, how using [Cypress](https://cypress.io), we are testing our user registration process at Tastewise.

# Usage

1.  Install using `npm`:

```
npm install --save-dev gmail-tester
```

2.  Save the Google Cloud Platform OAuth2 Authentication file named `credentials.json` inside an accessible directory (see instructions [below](https://github.com/levz0r/gmail-tester/blob/master/README.md#how-to-get-credentialsjson)).
3.  In terminal, run the following command:

```
node <node_modules>/gmail-tester/init.js <path-to-credentials.json> <path-to-token.json> <target-email>
```

`<path-to-credentials.json>` Is the path to OAuth2 Authentication file.<br/>
`<path-to-token.json>` Is the path to OAuth2 token. If it doesn't exist, the script will create it.<br/>
The script will prompt you to go to google.com to activate a token.
Go to the given link, and select the account for `<target-email>`. Grant permission to view your email messages and settings. At the end of the process you should see the token:

<p align="center">
  
</p>

Hit the copy button and paste it to `init.js` script.
The process should look like this:

<p align="center">
  
</p>

# How to get credentials.json?

1.  Follow the instructions to [Create a client ID and client secret](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid). Make sure to select `Desktop app` for the application type.
2.  Once done, go to [https://console.cloud.google.com/apis/credentials?project=(project-name)&folder&organizationId](<https://console.cloud.google.com/apis/credentials?project=(project-name)&folder&organizationId>) and download the OAuth2 credentials file, as shown in the image below. Make sure to replace `(project-name)` with your project name.

    <p align="center">
      
    </p>

    The `credentials.json` file should look like this:<p align="center">
    

    </p>

3.  Make sure the [Gmail API is activated](https://console.developers.google.com/apis/library/gmail.googleapis.com) for your account.

4.  **Configure OAuth co

---

## cristianzsh/youtube-video-maker ⭐235

**URL**: https://github.com/cristianzsh/youtube-video-maker

**Description**: :video_camera: A tool for automatic video creation and uploading on YouTube

# YouTube Video Maker

A tool for automatic video creation and uploading on YouTube.

![](examples/execution.gif)

### Result:

![](examples/youtube_video.png)

![](examples/youtube_video_tags.png)

## Getting Started

These instructions will show you how this tool works and how to have the project up and running on your local machine.

### Prerequisites

FFmpeg (version used to build this tool: 4.1.1-1)

```
$ sudo apt-get install ffmpeg   # on Debian based systems
$ sudo yum install ffmpeg       # on Red Hat based systems
```

Python libraries:

```
$ sudo pip3 install google_images_download==2.5.0
$ sudo pip3 install wikipedia==1.4.0
$ sudo pip3 install nltk==3.4.5
$ sudo pip3 install watson_developer_cloud==2.8.0
$ sudo pip3 install google-api-python-client==1.7.8
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

You will need to put your Watson API keys in the ``` searchrobot.py ``` file:
```
...
iam_apikey = "YOUR_API_KEY_HERE",
url = "YOUR_URL_HERE"
...
```

And your Google API keys in the ``` clients_secret.json ``` file:
```
...
"client_id": "YOUR_CLIENT_ID_HERE",
"client_secret": "YOUR_CLIENT_SECRET_HERE",
...
```

### Run the main file

After completing all the settings, just run the main file:
```
$ cd youtube-video-maker/src
$ python3 yvm.py
```

# How it works?

The program behaves as follows:
 * 1. Get the Wikipedia search term and the prefix;
 * 2. Get the first sentences from the Wikipedia summary which corresponds to the search term;
 * 3. Remove unnecessary information;
 * 4. Send each sentence to Watson to get the corresponding keywords;
 * 5. Download some images from Google Images based on the keywords;
 * 6. Rename and convert the images to JPG;
 * 7. Make the video, add the sentences as subtitles and add a music;
 * 8. Send the final video to YouTube with title, description and tags.

NOTE: All the files (images, videos and subtitles) are saved in the user's folder, in a directory with the search term name.

Example: [final_video.mp4](examples/final_video.mp4)

# Bugs to fix:
 * Get better images;
 * Correct the error that causes the fifth subtitle to be skipped.

### Other information

Project inspired by [video-maker](https://github.com/filipedeschamps/video-maker), by [filipedeschamps](https://github.com/filipedeschamps)

Music extracted from: [https://www.youtube.com/watch?v=LeV4u5Y-3ac](https://www.youtube.com/watch?v=LeV4u5Y-3ac)

Original video upload code: [https://developers.google.com/youtube/v3/guides/uploading_a_video?hl=en](https://developers.google.com/youtube/v3/guides/uploading_a_video?hl=en)

---

## int128/gpup ⭐219

**URL**: https://github.com/int128/gpup

**Description**: A command to upload photos and movies to Google Photos Library using the official Google Photos Library API

# gpup 

A command to upload photos and movies to your Google Photos Library.


## Getting Started

### Setup

You can install this from brew tap or [releases](https://github.com/int128/gpup/releases).

```sh
brew tap int128/gpup
brew install gpup
```

Setup your API access by the following steps:

1. Open https://console.cloud.google.com/apis/library/photoslibrary.googleapis.com/
1. Enable Photos Library API.
1. Open https://console.cloud.google.com/apis/credentials
1. Create an OAuth client ID where the application type is other.
1. Run `gpup` and follow the instruction as follows.

```
% gpup
2018/09/13 15:38:13 Skip reading ~/.gpupconfig: Could not open ~/.gpupconfig: open /user/.gpupconfig: no such file or directory
2018/09/13 15:38:13 Setup your API access by the following steps:

1. Open https://console.cloud.google.com/apis/library/photoslibrary.googleapis.com/
1. Enable Photos Library API.
1. Open https://console.cloud.google.com/apis/credentials
1. Create an OAuth client ID where the application type is other.

Enter your OAuth client ID (e.g. xxx.apps.googleusercontent.com): YOUR_CLIENT_ID.apps.googleusercontent.com
Enter your OAuth client secret: YOUR_CLIENT_SECRET
2018/09/13 15:38:22 Saved credentials to ~/.gpupconfig
2018/09/13 15:38:22 Error: Nothing to upload
```

### Upload files to the library

To upload files in a folder to your Google Photos library:

```
$ gpup my-photos/
2018/06/14 10:28:40 The following 2 files will be uploaded:
  1: my-photos/travel.jpg
  2: my-photos/lunch.jpg
2018/06/14 10:28:40 Open http://localhost:8000 for authorization
2018/06/14 10:28:43 GET /
2018/06/14 10:28:49 GET /?state=...&code=...
2018/06/14 10:28:49 Saved token to ~/.gpupconfig
2018/06/14 10:28:49 Queued 2 file(s)
2018/06/14 10:28:49 Uploading travel.jpg
2018/06/14 10:28:49 Uploading lunch.jpg
2018/06/14 10:28:52 Adding 2 file(s) to the library
```

It opens the browser and you can log in to the provider.
And then it uploads files concurrently.

You can specify URLs as well.

```sh
gpup https://www.example.com/image.jpg
```

### Upload files to an album

You can upload files to the album by `-a` option.
If the album does not exist, it will be created.

```sh
gpup -a "My Album" my-photos/
```

You can upload files to a new album by `-n` option.

```sh
gpup -n "My Album" my-photos/
```


## Usage

```
Usage:
  gpup [OPTIONS] <FILE | DIRECTORY | URL>...

Application Options:
  -a, --album=TITLE                 Add files to the album or a new album if it does not exist
  -n, --new-album=TITLE             Add files to a new album
      --request-header=KEY:VALUE    Add the header on fetching URLs
      --request-auth=USER:PASS      Add the basic auth header on fetching URLs
      --gpupconfig=                 Path to the config file (default: ~/.gpupconfig) [$GPUPCONFIG]
      --debug                       Enable request and response logging [$DEBUG]

Options read from gpupconfig:
      --google-client-id=           Google API client ID [$GOOGLE_

---

## Kubessandra/react-google-calendar-api ⭐214

**URL**: https://github.com/Kubessandra/react-google-calendar-api

**Description**: An api to manage your google calendar

# react-google-calendar-api

![Build Status](https://travis-ci.com/Insomniiak/react-google-calendar-api.svg?branch=master)
![npm (custom registry)](https://img.shields.io/npm/l/express.svg?registry_uri=https%3A%2F%2Fregistry.npmjs.com)
![npm (downloads)](https://img.shields.io/npm/dy/react-google-calendar-api.svg?style=popout)


An api to manage your google calendar

## Install

Npm

```
npm install --save react-google-calendar-api
```

yarn

```
yarn add react-google-calendar-api
```

## Use (Javascript / Typescript)

You will need to enable the "Google Calendar API"(https://console.developers.google.com/flows/enableapi?apiid=calendar.)
You will need a clientId and ApiKey from Google(https://developers.google.com/workspace/guides/create-credentials)

```javascript
import ApiCalendar from "react-google-calendar-api";

const config = {
  clientId: "<CLIENT_ID>",
  apiKey: "<API_KEY>",
  scope: "https://www.googleapis.com/auth/calendar",
  discoveryDocs: [
    "https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest",
  ],
};

const apiCalendar = new ApiCalendar(config);
```

## Setup

### handleAuthClick:

```javascript
    /**
     * Sign in with a Google account.
     * @returns {any} A Promise that is fulfilled with the GoogleUser instance when the user successfully authenticates and grants the requested scopes, or rejected with an object containing an error property if an error happened
     */
    public handleAuthClick(): void
```

### handleSignOutClick:

```javascript
    /**
     * Sign out user google account
     */
    public handleSignoutClick(): void
```

#### Example

```javascript
  import React, {ReactNode, SyntheticEvent} from 'react';
  import ApiCalendar from 'react-google-calendar-api';

  const config = {
    "clientId": "<CLIENT_ID>",
    "apiKey": "<API_KEY>",
    "scope": "https://www.googleapis.com/auth/calendar",
    "discoveryDocs": [
      "https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"
    ]
  }

  const apiCalendar = new ApiCalendar(config)

  export default class DoubleButton extends React.Component {
      constructor(props) {
        super(props);
        this.handleItemClick = this.handleItemClick.bind(this);
      }

      public handleItemClick(event: SyntheticEvent<any>, name: string): void {
        if (name === 'sign-in') {
          apiCalendar.handleAuthClick()
        } else if (name === 'sign-out') {
          apiCalendar.handleSignoutClick();
        }
      }

      render(): ReactNode {
        return (
              <button
                  onClick={(e) => this.handleItemClick(e, 'sign-in')}
              >
                sign-in
              </button>
              <button
                  onClick={(e) => this.handleItemClick(e, 'sign-out')}
              >
                sign-out
              </button>
          );
      }
  }
```

### setCalendar:

```javascript
    /**
     * Set the default attribute calendar
     * @param {string} newCalendar ID.
     */
    public s

---

## SachinAgarwal1337/google-places-api ⭐190

**URL**: https://github.com/SachinAgarwal1337/google-places-api

**Description**: This is a PHP wrapper for Google Places API Web Service. And is Laravel Framework friendly.



---

## dhruvldrp9/Google-Meet-Bot ⭐153

**URL**: https://github.com/dhruvldrp9/Google-Meet-Bot

**Description**: This project is a Python bot that automates the process of logging into Gmail, joining a Google Meet, recording the audio of the meeting, and then generating a summary, key points, action items, and sentiment analysis of the meeting. 



---

## sprawz/gtm-mcp-server ⭐143

**URL**: https://github.com/sprawz/gtm-mcp-server

**Description**: An MCP server for Google Tag Manager. Connect it to your LLM, authenticate once, and start managing GTM through natural language.



---

## dyaskur/google-chat-poll ⭐133

**URL**: https://github.com/dyaskur/google-chat-poll

**Description**: Absolute Poll - Google Chat Apps



---

