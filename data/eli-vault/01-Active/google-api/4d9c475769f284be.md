---
id: 4d9c475769f284be
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: []
containmentHash: 959cf9e0abc4c41fca9e
createdAt: 1786051356392
embeddingSig: "4194:zoom:zoom|7749:4194:zoom|coordinates:search:7749|default:radius:float|float:search:radius|level:default:radius|radius:float:search|radius:meters:default|search:7749:4194|search:radius:meters|zoom:level:default|zoom:zoom:level"
---
Coordinates for search, e.g., '37.7749,-122.4194'
  -zoom int          Zoom level 0-21 (default: 15)
  -radius float      Search radius in meters (default: 10000)
  -grid-bbox string  Bounding box for grid scraping, format: "minLat,minLon,maxLat,maxLon"
  -grid-cell float   Grid cell size in km (default: 1.0, used with -grid-bbox)
Web Server:
  -web               Run web server mode