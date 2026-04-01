// Backend API Response Format
// These are the TypeScript types your React components should expect

// When frontend calls POST http://localhost:8000/api/analyze
export const exampleAnalysisResponse = {
  "task": {
    "original_text": "washing car",
    "cleaned_text": "Washing Car",
    "activity": "washing car",
    "classification": "Outdoor",  // "Indoor" | "Outdoor"
    "confidence": 0.67,            // 0.0 - 1.0
    "reasoning": "Classified using keyword matching (Demo Mode)",
    "needs_clarification": false,  // true if input unclear
    "issue": null,                 // Problem description if needs_clarification
    "suggested_activity": null,    // Auto-judge suggestion (if unclear)
    "suggested_classification": null,
    "suggestion_confidence": 0.0
  },
  "weather": {
    "city": "New York",
    "country": "DEMO",
    "latitude": 40.7128,
    "longitude": -74.006,
    "temperature": 18.0,
    "feels_like": 16.0,
    "humidity": 51,                // 0-100%
    "rain_1h": 0.0,                // mm
    "is_raining": false,
    "wind_speed": 9.0,             // m/s
    "wind_mph": 20.1,              // mph for UI display
    "condition": "Clouds",         // "Clear", "Clouds", "Rain", etc
    "description": "scattered clouds",
    "icon_code": "03d",            // OpenWeather icon code
    "units": "metric",
    "temp_unit": "°C"
  },
  "score_result": {
    "score": 70,                   // 0-100
    "classification": "Outdoor",
    "weather_factors": [
      "💨 Wind: 20.1 mph",
      "☔ No rain"
    ],
    "bonuses": [],                 // Array of FactorDetail
    "penalties": [
      {
        "name": "High winds",
        "value": -30,              // negative = penalty
        "description": "Wind may affect outdoor activities"
      }
    ],
    "recommendation": "😊 Good conditions with minor considerations."
  },
  "alternatives": [
    ["📖 Reading", "Expand your knowledge"],
    ["🎮 Gaming", "Entertainment indoors"],
    ["🧘 Yoga", "Relaxation activity"]
  ]
};

// BREAKING DOWN THE RESPONSE FOR YOUR COMPONENTS:

// For TaskCard component:
const taskInfo = exampleAnalysisResponse.task;
// - Display original_text as title
// - Show classification badge (color-coded: Blue=Outdoor, Green=Indoor)
// - Show confidence progress bar (0-100%)
// - IF needs_clarification: Show red warning with issue text
// - IF suggested_activity: Show green suggestion bubble with suggestion_confidence%

// For WeatherCard component:
const weatherInfo = exampleAnalysisResponse.weather;
// - Temperature: 18°C (feels like 16°C)
// - Condition icon: Use icon_code or condition text
// - Grid of 6 items:
//   1. Temperature: 18°C
//   2. Feels Like: 16°C
//   3. Humidity: 51%
//   4. Wind: 20.1 mph
//   5. Rain: 0mm (or "No rain")
//   6. Location: 40.71°N, 74.01°W

// For ScoreCard component:
const scoreInfo = exampleAnalysisResponse.score_result;
// - Large circular score: 70/100
// - Color coding: 
//   - 0-30: Red 🔴
//   - 31-65: Yellow 🟡
//   - 66-85: Blue 🔵
//   - 86-100: Green 🟢
// - Show weather_factors as list
// - Show bonuses section (if any)
// - Show penalties section (if any)
// - Show recommendation text

// For AlternativesCard component:
const alternatives = exampleAnalysisResponse.alternatives;
// - Each pair is [activity, description]
// - Display as pills/buttons in responsive grid
// - On hover/click: User can select alternative

// UNCLEAR INPUT EXAMPLE:
export const exampleUnclearInputResponse = {
  "task": {
    "original_text": "doing homewo",
    "cleaned_text": "Doing Homewo",
    "activity": "doing homewo",
    "classification": "Indoor",
    "confidence": 0.15,            // ← LOW confidence indicator
    "reasoning": "Input too incomplete",
    "needs_clarification": true,   // ← FLAG: Input unclear
    "issue": "Your input appears incomplete or has a typo",
    "suggested_activity": "doing homework",    // ← Auto-suggestion
    "suggested_classification": "Indoor",
    "suggestion_confidence": 0.92  // ← HIGH confidence in suggestion
  },
  // ... other fields same
};

// When displaying unclear input:
// 1. Show red warning box with issue text
// 2. Show suggestion: "Did you mean: doing homework? (92% match)"
// 3. Option to click suggestion to re-analyze

// NOTES FOR FRONTEND DEVELOPERS:
// 1. All score values are 0-100 integers
// 2. All confidence values are 0-1.0 floats
// 3. Classification is always "Indoor" or "Outdoor"
// 4. Temperature unit depends on weather.units ("metric"=°C, "imperial"=°F)
// 5. Icons: Use emojis or icon library (Lucide, FontAwesome)
// 6. Alternatives are always provided (never empty)
// 7. If needs_clarification=true, suggested_activity will be populated
// 8. Wind speed provided in both m/s and mph for flexibility

// TESTING WITHOUT NODE.JS (if stuck on installation):
// You can manually test responses using:
// curl -X POST http://localhost:8000/api/analyze \
//   -H "Content-Type: application/json" \
//   -d '{"activity_text":"washing car","city":"New York","use_demo_weather":true}'

// Or in PowerShell:
// $body = @{activity_text='washing car';city='New York';use_demo_weather=$true} | ConvertTo-Json
// Invoke-WebRequest -Uri 'http://localhost:8000/api/analyze' -Method POST -ContentType 'application/json' -Body $body | Select-Object -ExpandProperty Content | ConvertFrom-Json
