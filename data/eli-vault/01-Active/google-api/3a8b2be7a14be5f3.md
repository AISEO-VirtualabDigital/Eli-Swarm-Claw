---
id: 3a8b2be7a14be5f3
source: "google-maps-places-api-tools.md"
"title: Google Maps, Places & Geolocation API Tools"
category: google-api
skillTags: ["tool", "code"]
containmentHash: 8b0f5a53aabde31e1dbd
createdAt: 1786051356386
embeddingSig: "googleapis:maps:your|html:script:https|https:maps:googleapis|libraries:places:script|library:your:project|load:library:your|maps:googleapis:maps|maps:your:libraries|project:html:script|script:https:maps|your:libraries:places|your:project:html"
---
pt/)
Load the library in your project

```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places"></script>
```
Create your component

```js
import React from 'react';
import PlacesAutocomplete, {
  geocodeByAddress,
  getLatLng,
} from 'react-places-autocomplete';
class LocationSearchInput extends React.Component {
  constructor(props) {
    super(props);