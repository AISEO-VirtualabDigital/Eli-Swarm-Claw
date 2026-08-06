# Google Maps, Places & Geolocation API Tools

Libraries and components for Google Maps integration, Places Autocomplete, Geocoding, and reverse image search.

## fullstackreact/google-maps-react ⭐1,638

**URL**: https://github.com/fullstackreact/google-maps-react

**Description**: Companion code to the "How to Write a Google Maps React Component" Tutorial

<p align="center">
  
</p>

# Google Map React Component Tutorial 

> A declarative Google Map React component using React, lazy-loading dependencies, current-location finder and a test-driven approach by the [Fullstack React](https://fullstackreact.com) team.

See the [demo](https://fullstackreact.github.io/google-maps-react) and [accompanying blog post](https://www.fullstackreact.com/articles/how-to-write-a-google-maps-react-component/).

## Quickstart

First, install the library:

```shell
npm install --save google-maps-react
```
## Automatically Lazy-loading Google API

The library includes a helper to wrap around the Google maps API. The `GoogleApiWrapper` Higher-Order component accepts a configuration object which *must* include an `apiKey`. See [lib/GoogleApi.js](https://github.com/fullstackreact/google-maps-react/blob/master/src/lib/GoogleApi.js#L4) for all options it accepts.

```javascript
import {GoogleApiWrapper} from 'google-maps-react';

// ...

export class MapContainer extends React.Component {}

export default GoogleApiWrapper({
  apiKey: (YOUR_GOOGLE_API_KEY_GOES_HERE)
})(MapContainer)
```

Alternatively, the `GoogleApiWrapper` Higher-Order component can be configured by passing a function that will be called with whe wrapped component's `props` and should returned the configuration object.

```javascript
export default GoogleApiWrapper(
  (props) => ({
    apiKey: props.apiKey,
    language: props.language,
  }
))(MapContainer)
```

If you want to add a loading container _other than the default_ loading container, simply pass it in the HOC, like so:

```javascript
const LoadingContainer = (props) => (
  <div>Fancy loading container!</div>
)

export default GoogleApiWrapper({
  apiKey: (YOUR_GOOGLE_API_KEY_GOES_HERE),
  LoadingContainer: LoadingContainer
})(MapContainer)
```

## Sample Usage With Lazy-loading Google API:

```javascript
import {Map, InfoWindow, Marker, GoogleApiWrapper} from 'google-maps-react';

export class MapContainer extends Component {
  render() {
    return (
      <Map google={this.props.google} zoom={14}>

        <Marker onClick={this.onMarkerClick}
                name={'Current location'} />

        <InfoWindow onClose={this.onInfoWindowClose}>
            <div>
              <h1>{this.state.selectedPlace.name}</h1>
            </div>
        </InfoWindow>
      </Map>
    );
  }
}

export default GoogleApiWrapper({
  apiKey: (YOUR_GOOGLE_API_KEY_GOES_HERE)
})(MapContainer)
```
*Note: [Marker](#marker) and [InfoWindow](#infowindow--sample-event-handler-functions) components are disscussed below.*

![](http://d.pr/i/C7qr.png)

## Examples

Check out the example site at: [http://fullstackreact.github.io/google-maps-react](http://fullstackreact.github.io/google-maps-react)

## Additional Map Props
The Map component takes a number of optional props.

Zoom: (Shown Above) takes a number with the higher value representing a tighter focus on the map's center.

Style: Takes CSS style object - commonly width 

---

## hibiken/react-places-autocomplete ⭐1,375

**URL**: https://github.com/hibiken/react-places-autocomplete

**Description**: React component for Google Maps Places Autocomplete

## We are looking for maintainers!
In order to ensure active development going forward, we are looking for maintainers to join the project. [Please contact the project owner if you are interested.](https://github.com/hibiken/react-places-autocomplete/issues/296#issuecomment-583764730)

# React Places Autocomplete



A React component to build a customized UI for Google Maps Places Autocomplete

### Demo

Live demo: [hibiken.github.io/react-places-autocomplete/](https://hibiken.github.io/react-places-autocomplete/)

### Features

1. Enable you to easily build a customized autocomplete dropdown powered by [Google Maps Places Library](https://developers.google.com/maps/documentation/javascript/places)
2. [Utility functions](#utility-functions) to geocode and get latitude and longitude using [Google Maps Geocoder API](https://developers.google.com/maps/documentation/javascript/geocoding)
3. Full control over rendering to integrate well with other libraries (e.g. Redux-Form)
4. Mobile friendly UX
5. WAI-ARIA compliant
6. Support Asynchronous Google script loading

### Installation

To install the stable version

```sh
npm install --save react-places-autocomplete
```

React component is exported as a default export

```js
import PlacesAutocomplete from 'react-places-autocomplete';
```

utility functions are named exports

```js
import {
  geocodeByAddress,
  geocodeByPlaceId,
  getLatLng,
} from 'react-places-autocomplete';
```

### Getting Started

<a name="load-google-library"></a>
To use this component, you are going to need to load [Google Maps JavaScript API](https://developers.google.com/maps/documentation/javascript/)

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
    this.state = { address: '' };
  }

  handleChange = address => {
    this.setState({ address });
  };

  handleSelect = address => {
    geocodeByAddress(address)
      .then(results => getLatLng(results[0]))
      .then(latLng => console.log('Success', latLng))
      .catch(error => console.error('Error', error));
  };

  render() {
    return (
      <PlacesAutocomplete
        value={this.state.address}
        onChange={this.handleChange}
        onSelect={this.handleSelect}
      >
        {({ getInputProps, suggestions, getSuggestionItemProps, loading }) => (
          <div>
            <input
              {...getInputProps({
                placeholder: 'Search Places ...',
                className: 'location-search-input',
              })}
            />
            <div className="autocomplete-dropdown-container">
              {loa

---

## SachinAgarwal1337/google-places-api ⭐190

**URL**: https://github.com/SachinAgarwal1337/google-places-api

**Description**: This is a PHP wrapper for Google Places API Web Service. And is Laravel Framework friendly.



---

## somanchiu/Keyless-Google-Maps-API ⭐123

**URL**: https://github.com/somanchiu/Keyless-Google-Maps-API

**Description**: Use the Google Maps JavaScript API without API KEY in any domain



---

