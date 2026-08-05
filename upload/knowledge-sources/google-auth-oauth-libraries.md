# Google Authentication & OAuth Libraries

Libraries for Google Sign-In, OAuth 2.0, and authentication across React, Angular, Vue, React Native, and Elixir.

## anthonyjgrove/react-google-login ⭐1,831

**URL**: https://github.com/anthonyjgrove/react-google-login

**Description**: A React Google Login Component

```diff
- This package is no longer maintained.
```

# React Google Login

> A Google oAUth Sign-in / Log-in Component for React

## Storybook

[Demo Link](https://anthonyjgrove.github.io/react-google-login/)

## Install
```
npm install react-google-login
```

## How to use
```js
import React from 'react';
import ReactDOM from 'react-dom';
import GoogleLogin from 'react-google-login';
// or
import { GoogleLogin } from 'react-google-login';


const responseGoogle = (response) => {
  console.log(response);
}

ReactDOM.render(
  <GoogleLogin
    clientId="658977310896-knrl3gka66fldh83dao2rhgbblmd4un9.apps.googleusercontent.com"
    buttonText="Login"
    onSuccess={responseGoogle}
    onFailure={responseGoogle}
    cookiePolicy={'single_host_origin'}
  />,
  document.getElementById('googleButton')
);
```

## Google button without styling or custom button
```js
ReactDOM.render(
  <GoogleLogin
    clientId="658977310896-knrl3gka66fldh83dao2rhgbblmd4un9.apps.googleusercontent.com"
    render={renderProps => (
      <button onClick={renderProps.onClick} disabled={renderProps.disabled}>This is my custom Google button</button>
    )}
    buttonText="Login"
    onSuccess={responseGoogle}
    onFailure={responseGoogle}
    cookiePolicy={'single_host_origin'}
  />,
  document.getElementById('googleButton')
);
```

## Stay Logged in
`isSignedIn={true}` attribute will call `onSuccess` callback on load to keep the user signed in.
```jsx
<GoogleLogin
  clientId="658977310896-knrl3gka66fldh83dao2rhgbblmd4un9.apps.googleusercontent.com"
  onSuccess={responseGoogle}
  isSignedIn={true}
/>
```

## Login Hook
```js
import { useGoogleLogin } from 'react-google-login'

const { signIn, loaded } = useGoogleLogin({
    onSuccess,
    onAutoLoadFinished,
    clientId,
    cookiePolicy,
    loginHint,
    hostedDomain,
    autoLoad,
    isSignedIn,
    fetchBasicProfile,
    redirectUri,
    discoveryDocs,
    onFailure,
    uxMode,
    scope,
    accessType,
    responseType,
    jsSrc,
    onRequest,
    prompt
  })
```
## Logout Hook
```js
import { useGoogleLogout } from 'react-google-login'

const { signOut, loaded } = useGoogleLogout({
    jsSrc,
    onFailure,
    clientId,
    cookiePolicy,
    loginHint,
    hostedDomain,
    fetchBasicProfile,
    discoveryDocs,
    uxMode,
    redirectUri,
    scope,
    accessType,
    onLogoutSuccess
  })
```
## onSuccess callback

If responseType is not 'code', callback will return the GoogleAuth object.

If responseType is 'code', callback will return the authorization code that can
be used to retrieve a refresh token from the server.

If you use the hostedDomain param, make sure to validate the id_token (a JSON web token) returned by Google on your backend server:
 1. In the `responseGoogle(response) {...}` callback function, you should get back a standard JWT located at `response.tokenId` or `res.getAuthResponse().id_token`
 2. Send this token to your server (preferably as an `Authorization` header)
 3. Have your server deco

---

## dwyl/elixir-auth-google ⭐290

**URL**: https://github.com/dwyl/elixir-auth-google

**Description**: 👤Minimalist Google OAuth Authentication for Elixir Apps. Tested, Documented & Maintained. Setup in 5 mins. 🚀

<div align="center">

# `elixir-auth-google`

The _easiest_ way to add Google OAuth authentication to your Elixir Apps.

![sign-in-with-google-buttons](https://user-images.githubusercontent.com/194400/69637172-07a67900-1050-11ea-9e25-2b9e84a49d91.png)

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/dwyl/elixir-auth-google/ci.yml?label=build&style=flat-square&branch=main)

<!--  -->

</div>

# _Why_? 🤷

We needed a **_much_ simpler**
and **_extensively_ documented** way
to add "_**Sign-in** with **Google**_"
capability to our Elixir App(s). <br />

# _What_? 💭

An Elixir package that seamlessly handles
Google OAuth2 Authentication/Authorization
in as few steps as possible. <br />
Following best practices for security & privacy
and avoiding complexity
by having sensible defaults for all settings.


> We built a lightweight solution
that only does _one_ thing
and is easy for complete beginners to understand/use. <br />
There were already _several_ available options
for adding Google Auth to apps on
[hex.pm/packages?search=google](https://hex.pm/packages?search=google) <br />
that all added _far_ too many implementation steps (complexity)
and had incomplete docs (**`@doc false`**) and tests. <br />
e.g:
[github.com/googleapis/elixir-google-api](https://github.com/googleapis/elixir-google-api)
which is a
["_generated_"](https://github.com/googleapis/elixir-google-api/blob/master/scripts/generate_client.sh)
client and is considered "experimental". <br />
We have drawn inspiration from several sources
including code from other programming languages to build this package.
This result is _much_ simpler
than anything else
and has both step-by-step instructions
and a _complete working example_ App
including how to encrypt tokens for secure storage
to help you ship your app _fast_.


# _Who_? 👥

This module is for people building apps using Elixir/Phoenix
who want to ship the "Sign-in with Google" feature _faster_
and more maintainably.

It's targeted at _complete_ beginners
with no prior experience/knowledge
of auth "schemes" or "strategies". <br />
Just follow the detailed instructions
and you'll be up-and running in 5 minutes.


# _How_? ✅

You can add Google Authentication to your Elixir App
using **`elixir_auth_google`** <br />
in under **5 minutes**
by following these **5 _easy_ steps**:

## 1. Add the hex package to `deps` 📦

Open your project's **`mix.exs`** file
and locate the **`deps`** (dependencies) section. <br />
Add a line for **`:elixir_auth_google`** in the **`deps`** list:

```elixir
def deps do
  [
    {:elixir_auth_google, "~> 1.6.9"}
  ]
end
```

Once you have added the line to your **`mix.exs`**,
remember to run the **`mix deps.get`** command
in your terminal
to _download_ the dependencies.


## 2. Create Google APIs Application OAuth2 Credentials 🆕

Create a Google Application if you don't already have one,
generate the OAuth2 Credentials for the application
and save the credentials as environment varia

---

## joonhocho/react-native-google-sign-in ⭐216

**URL**: https://github.com/joonhocho/react-native-google-sign-in

**Description**: React Native Wrapper for Latest Google Sign-In OAuth SDK / API

# React Native Wrapper for Latest Google Sign-In SDK

https://github.com/devfd/react-native-google-signin is not working and is not being maintained anymore ([See Issue](https://github.com/devfd/react-native-google-signin/issues/182)), so I created this one myself.
It uses the latest [Google Sign-In SDK](https://developers.google.com/identity/).

For LinkedIn SDK, check out [joonhocho/react-native-linkedin-sdk](https://github.com/joonhocho/react-native-linkedin-sdk)

## Getting started

Tested with React Native 0.39 and 0.40. Also, see [Tested Environments](#tested-environments).
Let me know if some instructions are missing.

`$ react-native install react-native-google-sign-in`


## Android
Follow Google's official instructions for [Android](https://developers.google.com/identity/sign-in/android/start-integrating).

Follow everything from the instructions with the following modifications.
Some of the following modifications should be done by `react-native install` automatically. If not, do it yourself:
 - Move `google-services.json` to `{YourApp}/android/app/google-services.json`.
 
 - Add to your `{YourApp}/android/settings.gradle`:
```
include ':react-native-google-sign-in'
project(':react-native-google-sign-in').projectDir = new File(rootProject.projectDir, '../node_modules/react-native-google-sign-in/android')
```

 - Modify your `{YourApp}/android/build.gradle`:
```
dependencies {
    classpath 'com.android.tools.build:gradle:2.2.3' // This may need to be updated to >= 2.2.3.
    classpath 'com.google.gms:google-services:3.0.0' // Add this
}
```

 - Modify your `{YourApp}/android/app/build.gradle`:
```
dependencies {
    compile(project(":react-native-google-sign-in")) { // ADD this
        exclude group: "com.google.android.gms"
    } 
    ...your modules...
    compile "com.google.android.gms:play-services-auth:10.0.1" // Add this, not 9.8.0 (from instructions).
    compile "com.facebook.react:react-native:+"
}

apply plugin: "com.google.gms.google-services" // Add this after dependencies.
```

 - Modify your `{YourApp}/android/app/src/main/java/com/{YourApp}/MainApplication.java`:
```
import com.reactlibrary.googlesignin.RNGoogleSignInPackage; // Add this.

...in your class MainApplication...
        @Override
        protected List<ReactPackage> getPackages() {
            return Arrays.<ReactPackage>asList(
                    new MainReactPackage(),
                    new RNGoogleSignInPackage(), // Add this.
                    ...other packages...
            );
        }
```


## iOS

### (prerequisite) Setup Swift Bridging Header
- Make sure you have a Swift Bridging Header for your project. Here's [how to create one](http://www.learnswiftonline.com/getting-started/adding-swift-bridging-header/) if you don't.
- ![](https://i.imgur.com/1XgTv5h.png)

### Manually download and install Google SignIn SDK (Without CocoaPods)
- At the time of writing, `Google Sign-In SDK 4.1.0` is the latest.
- Follow Google's official instructions, [Ins

---

