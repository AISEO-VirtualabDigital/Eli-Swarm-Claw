# Google API Client Libraries — Reference

Comprehensive reference for official and popular Google API client libraries.

## googleapis/google-api-nodejs-client ⭐12,218

**URL**: https://github.com/googleapis/google-api-nodejs-client

**Language**: TypeScript

**Description**: Google's officially supported Node.js client library for accessing Google APIs. Support for authorization and authentication with OAuth 2.0, API Keys and JWT (Service Tokens) is included. 

# Google APIs Node.js Client

[![npm version][npmimg]][npm]
[![Downloads][downloadsimg]][downloads]
[![Known Vulnerabilities][snyk-image]][snyk-url]

[Node.js][node] client library for using Google APIs. Support for authorization and authentication with OAuth 2.0, API Keys and JWT tokens is included.

* [Google APIs](#google-apis)
* [Getting started](#getting-started)
  * [Installation](#installation)
  * [Using the client library](#using-the-client-library)
  * [Samples](#samples)
  * [API Reference](#api-reference)
* [Authentication and authorization](#authentication-and-authorization)
  * [OAuth2 client](#oauth2-client)
  * [Using API keys](#using-api-keys)
  * [Application default credentials](#application-default-credentials)
  * [Service account credentials](#service-account-credentials)
  * [Setting global or service-level auth](#setting-global-or-service-level-auth)
* [Usage](#usage)
  * [Specifying request body](#specifying-request-body)
  * [Media uploads](#media-uploads)
  * [Request Options](#request-options)
  * [Using a Proxy](#using-a-proxy)
  * [Supported APIs](#getting-supported-apis)
  * [TypeScript](#typescript)
  * [HTTP/2](#http2)
* [License](#license)
* [Contributing](#contributing)
* [Questions/problems?](#questionsproblems)

## Google APIs
The full list of supported APIs can be found on the [Google APIs Explorer][apiexplorer]. The API endpoints are automatically generated, so if the API is not in the list, it is currently not supported by this API client library.

### Working with Google Cloud Platform APIs?
When utilizing Google Cloud Platform APIs like Datastore, Cloud Storage, or Pub/Sub, it is advisable to leverage the @google-cloud client libraries. These libraries are purpose-built, idiomatic Node.js clients designed for specific Google Cloud Platform services. We recommend installing individual API packages, such as `@google-cloud/storage`. To explore a comprehensive list of Google Cloud Platform API-specific packages, please refer to https://cloud.google.com/nodejs/docs/reference.

### Support and maintenance
These client libraries are officially supported by Google. However, these libraries are considered complete and are in maintenance mode. This means that we will address critical bugs and security issues but will not add any new features. For Google Cloud Platform APIs, we recommend using [google-cloud-node](https://github.com/GoogleCloudPlatform/google-cloud-node) which is under active development.

This library supports the maintenance LTS, active LTS, and current release of node.js.  See the [node.js release schedule](https://github.com/nodejs/Release) for more information.

## Getting started

### Installation
This library is distributed on `npm`. In order to add it as a dependency, run the following command in your terminal:

```sh
npm install googleapis
```

If you need to reduce startup times, you can alternatively install a submodule as its own dependency. We make an effort to publish submodules that are __not__ in this [list](https://github.com/googleapis/google-cloud-node#google-cloud-nodejs-client-libraries). In order to add it as a dependency, run the following sample command in your terminal, replacing with your preferred API:

```sh
npm install @googleapis/docs
```

You can run [this search](https://www.npmjs.com/search?q=scope%3A@googleapis) on `npm`, to find a list of the submodules available.
### Using the client library

This is a very simple example. This creates a Blogger client and retrieves the details of a blog given the blog Id:

```js
const {google} = require('googleapis');

// Each API may support multiple versions. With this sample, we're getting
// v3 of the blogger API, and using an API key to authenticate.
const blogger = google.blogger({
  version: 'v3',
  auth: 'YOUR API KEY'
});

const params = {
  blogId: '3213900'
};

// get the blog details
blogger.blogs.get(params, (err, res) => {
  if (err) {
    console.error(err);
    throw err;
  }
  console.log(`The 

---

## LindaLawton/Google-Dotnet-Samples ⭐247

**URL**: https://github.com/LindaLawton/Google-Dotnet-Samples

**Language**: N/A

**Description**: Unoffical Samples for the Google APIs .Net client library.  

# Unoffical Samples for the Google APIs .Net client library.  #

Sample project for working with the diffrent Google APIs with .net

Projects all use the Google .net client library which can be found on 

* [NuGet Packages](https://www.nuget.org/packages?q=Tags%3A%22Google%22) 
* Source Code Google [google-api-dotnet-client](https://github.com/google/google-api-dotnet-client)

## Disclaimer

Google has not created these sample projects, or the tutorials that go along with them.  They were all created by me.


## Installing client library with NuGet

All of the Google NuGet packages needed can be found here [NuGet Packages](https://www.nuget.org/packages?q=Tags%3A%22Google%22) 

## Contributing

These samples have been programmatically generated. Changes must be made in the T4 template files. Changes made in the samples themselves will be over written the next time the project is generated.

See [Contributing](CONTRIBUTING.md)

## License

Copyright 2017 DAIMTO ([Linda Lawton](https://twitter.com/LindaLawtonDK)) :  [www.daimto.com](http://www.daimto.com/)

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. See [LICENSE](https://github.com/LindaLawton/Google-APIs-PHP-Samples/blob/master/LICENSE)

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

## Tutorials

Tutorials for these projects can be found on [Daimto.com](http://www.daimto.com/)

---

## omarryhan/aiogoogle ⭐224

**URL**: https://github.com/omarryhan/aiogoogle

**Language**: Python

**Description**: Async Google API Client + Async Google Auth

<p align="center">
  
  <p align="center">
    <a href="https://github.com/omarryhan/aiogoogle/actions?query=workflow%3ACI"></a>
    <a href="https://github.com/omarryhan/aiogoogle"></a>
    <a href="https://github.com/python/black"></a>
    <a href="https://static.pepy.tech/badge/aiogoogle"></a>
    <a href="https://static.pepy.tech/badge/aiogoogle/month"></a>
  </p>
</p>

# Aiogoogle

**Async** Google API client

Aiogoogle makes it possible to access most of Google's public APIs which include:

- Google Calendar API
- Google Drive API
- Google Contacts API
- Gmail API
- Google Maps API
- Youtube API
- Translate API
- Google Sheets API
- Google Docs API
- Gogle Analytics API
- Google Books API
- Google Fitness API
- Google Genomics API
- Google Cloud Storage
- Kubernetes Engine API
- And [more](https://developers.google.com/apis-explorer)

## Documentation 📑

You can find the documentation [here](https://aiogoogle.readthedocs.io/en/latest/#).

---

## mscraftsman/generative-ai ⭐213

**URL**: https://github.com/mscraftsman/generative-ai

**Language**: C#

**Description**: Gemini SDK for .NET and ASP.NET Core enables developers to use Google's state-of-the-art generative AI models to build AI-powered features and applications.



---

