---
id: bc2ec781cc1fb72b
source: "google-auth-oauth-libraries.md"
"title: Google Authentication & OAuth Libraries"
category: google-api
skillTags: ["code"]
containmentHash: 58e946d382808b4cdff5
createdAt: 1786051355705
embeddingSig: "button:without:styling|cookiepolicy:single:host|document:getelementbyid:googlebutton|getelementbyid:googlebutton:google|google:button:without|googlebutton:google:button|host:origin:document|onfailure:responsegoogle:cookiepolicy|origin:document:getelementbyid|responsegoogle:cookiepolicy:single|responsegoogle:onfailure:responsegoogle|single:host:origin"
---
s={responseGoogle}
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