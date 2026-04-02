# Maps Module

**Location:** `services/maps.py`

## Purpose

Renders interactive Folium maps with weather overlays and geolocation markers for activity locations.

## Key Functions

### `render_map(lat, lon, city, weather)`

Creates an interactive map with weather information and user location.  
**Input:**

- Latitude, longitude
- City name
- WeatherData object

**Output:** Folium map object with interactive layers

## Map Features

### Base Layers

- CartoDB Dark (default)
- CartoDB Light
- OpenStreetMap

### Interactive Controls

- Fullscreen toggle
- Mini map (bottom-right)
- Mouse position display
- Layer selector

### Weather Overlay

- **Marker:** Location point with weather popup
- **Ring:** Weather intensity radius (2500-11500m)
- **Inner Focus Ring:** Highlighted area (500m-3800m)

### Marker Styling

- **Icon Color:** Based on weather condition
  - Blue: Raining
  - Orange: Clear
  - Gray: Other conditions
- **Popup:** Detailed weather info (temp, condition, wind, humidity)
- **Tooltip:** Quick city and temperature display

### Weather Intensity Calculation

Ring radius determined by:

```
intensity = min(1.0, (rain_1h / 5.0) + (wind_mph / 40.0))
ring_radius = 2500 + int(intensity * 9000)
```

Ring color:

- Cyan (#06b6d4): Not raining weather
- Blue (#3b82f6): Rainy weather

## Visual Elements

- Weather emoji in popup
- Structured HTML popup with styled information
- Color-coded rings for weather intensity
- Multi-layer tile options for different viewing preferences
