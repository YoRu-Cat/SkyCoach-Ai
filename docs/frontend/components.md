# Frontend Components Documentation

**Location:** `frontend/src/components/`

## Component Overview

### ActivityInput.tsx
**Purpose:** Form for entering activity description and location.

**Props:**
- `onAnalyze(activity: string, city: string)` - Callback on submit
- `isLoading: boolean` - Loading state

**Features:**
- Textarea for activity description with placeholder
- Quick activity suggestion buttons (chips)
- City/location input field
- Submit button with shimmer animation
- Auto-enable/disable based on input

**Styling:**
- Glassmorphism card with border animation
- Cyan focus highlighting
- Hover effects on chips with translation
- Responsive layout

---

### Header.tsx
**Purpose:** Top navigation and branding.

**Features:**
- SkyCoach AI logo/title
- Navigation structure
- Responsive header layout
- Consistent spacing with main content

---

### TaskCard.tsx
**Purpose:** Displays identified activity and classification.

**Props:**
- `analysis: TaskAnalysis` - Analyzed task data

**Displays:**
- Original and cleaned activity text
- Classification badge ("Indoor" or "Outdoor")
- Confidence indicator (0-100%)
- Reasoning/explanation

**Styling:**
- Card container with glow effect
- Color-coded classification badges
- Confidence progress bar

---

### WeatherCard.tsx
**Purpose:** Shows current weather conditions and location map.

**Props:**
- `weather: WeatherData` - Weather information

**Displays:**
- City and country
- Temperature with "feels like"
- Condition and description
- Humidity and wind speed
- Interactive map with location marker

**Map Integration:**
- OpenStreetMap iframe via `render_map()`
- Weather intensity visualization
- Zoom and interactive controls

---

### ScoreCard.tsx
**Purpose:** Displays detailed scoring breakdown.

**Props:**
- `score: SkyScoreResult` - Scoring result

**Displays:**
- Overall score (0-100)
- Weather factors affecting score
- Bonuses (positive adjustments)
- Penalties (negative adjustments)
- Recommendation message

**Styling:**
- Color-coded factors with emojis
- Bonus (green) and penalty (red) highlights

---

### ScoreGauge.tsx
**Purpose:** Animated SVG gauge showing score 0-100.

**Props:**
- `score: number` - Score value (0-100)

**Features:**
- Segmented arc design with gradient
- Animated needle with GSAP tweening (1.2s)
- Dashed background ring
- Smooth number animation from 0 to score
- Responsive sizing

**Animation:** Easing: power3.out, Duration: 1.2s

---

### AlternativesCard.tsx
**Purpose:** Suggests alternative activities.

**Props:**
- `alternatives: string[]` - List of suggestions
- `onUseSuggestion(activity: string)` - Callback when user selects suggestion

**Features:**
- Displays 3-4 alternative activity suggestions
- Click-to-use buttons
- Triggered based on current weather

---

### WeatherBackground.tsx
**Purpose:** Animated fullscreen background based on weather.

**Props:**
- `weather: WeatherData | undefined` - Current weather

**Features:**
- Condition-aware gradients:
  - Clear: Orange to blue gradient
  - Rainy: Gray-blue with movement
  - Thunderstorm: Dark purple with intensity
  - Snow: Light blue with particle effect
- Animated orbital elements
- Fog/breathing effects
- Fixed positioning behind all content
- Smooth condition transitions

**Animations:**
- Orbital A: 11s infinite rotation
- Orbital B: 14s infinite rotation
- Fog breathing effect

---

### AnalysisResult.tsx
**Purpose:** Container for all analysis components with entrance animation.

**Props:**
- `analysis: AnalysisResponse` - Complete analysis result
- `onUseSuggestion(activity: string)` - Callback for alternative selection

**Features:**
- Staggered GSAP animations on mount
- Panel fade-in with Y offset
- 0.1s stagger between panels
- Renders TaskCard, WeatherCard, ScoreCard, AlternativesCard

**Animation:**
- FromTo: opacity 0→1, y: 24→0
- Duration: 0.55s per panel
- Stagger: 0.1s between panels

---

## Shared Features

**Styling:**
- TailwindCSS utility classes
- Custom animation classes (globals.css)
- Glassmorphism effects (backdrop-filter, transparency)
- Responsive grid layout
- Dark theme (slate palette)

**Animations:**
- Shimmer button sweep
- Card border glow pulse
- Floating panel drift
- Score gauge needle rotation
- Panel entrance stagger
- Weather background orbits

**Colors:**
- Primary: Cyan (#06b6d4)
- Accent: Purple (#8b5cf6)
- Background: Slate-900, Slate-800
- Text: Slate-100, Slate-300
