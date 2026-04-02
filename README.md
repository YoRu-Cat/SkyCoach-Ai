# 🌤️ SkyCoach AI

A beautiful, intelligent weather-based activity advisor with a React frontend and FastAPI backend.

![SkyCoach AI](https://img.shields.io/badge/SkyCoach-AI-6366f1?style=for-the-badge&logo=cloud&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61dafb?style=for-the-badge&logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)

## ✨ Features

- 🧠 **AI-Powered Text Understanding** - Handles typos and messy input using GPT-4
- 🌡️ **Real-Time Weather Data** - Live weather from OpenWeatherMap API
- 📊 **Smart SkyScore Algorithm** - 0-100% activity recommendation score
- 🗺️ **Interactive Weather Map** - Folium-powered location visualization
- 🎨 **Stunning Glassmorphism UI** - Modern dark theme with animations
- 📜 **Activity History** - Track your recent analyses
- 💡 **Smart Recommendations** - Alternative activity suggestions
- 🕐 **Weather Forecast** - Upcoming hours preview
- ✨ **Smooth CSS Animations** - Beautiful transitions and effects

## 📚 Documentation

Complete documentation is available in the `/docs` folder:

- **[Architecture](docs/architecture/system_design.md)** - System design, data flow, and deployment
- **Backend Services:**
  - [AI Engine](docs/backend/ai_engine.md) - Task analysis and classification
  - [Auto-Judge](docs/backend/auto_judge.md) - Activity suggestion engine
  - [Scoring Engine](docs/backend/scoring_engine.md) - SkyScore calculation
  - [Maps](docs/backend/maps.md) - Interactive map rendering
  - [API Routes](docs/backend/api_routes.md) - REST API endpoints
- **Frontend Components:**
  - [Components](docs/frontend/components.md) - React UI components overview
  - [Services](docs/frontend/services.md) - API client and HTTP handling
  - [Hooks](docs/frontend/hooks.md) - Custom React hooks
- **Data & Models:**
  - [Data Models](docs/datasets/data_models.md) - Database schemas and types
  - [Activity Corpus](docs/datasets/activity_corpus.md) - 100+ activity dataset

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Language       │     │    Weather       │     │   Scoring       │
│  Engine         │     │    Engine        │     │   Engine        │
│  (OpenAI)       │     │  (OpenWeather)   │     │  (Decision      │
│                 │     │                  │     │   Matrix)       │
│  • Clean text   │     │  • Temperature   │     │  • Calculate    │
│  • Classify     │     │  • Rain/Wind     │     │    SkyScore     │
│    Indoor/      │────▶│  • Conditions    │────▶│  • Apply        │
│    Outdoor      │     │  • Location      │     │    penalties    │
│                 │     │                  │     │  • Add bonuses  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## 📋 Decision Matrix

| Task Type | Weather Factor | Impact |
|-----------|----------------|--------|
| 🏃 Outdoor | Rain > 0mm | ❌ **-80%** |
| 🏃 Outdoor | Wind > 15mph | ⚠️ **-30%** |
| 🏠 Indoor | Rain > 0mm | ✅ **+20%** |
| 🏠 Indoor | Temp > 30°C | ✅ **+10%** |

## 🚀 Quick Start

### 1. Clone & Install

```bash
# Navigate to project directory
cd "Project Ai"

# Install dependencies
pip install -r requirements.txt
```

### 2. Get API Keys (Optional)

**OpenAI API Key:**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account and generate an API key
3. Copy the key for later

**OpenWeatherMap API Key:**
1. Go to [openweathermap.org/api](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard

### 3. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 🎮 Demo Mode

Don't have API keys? No problem! The app includes a **Demo Mode** that works without any API keys:

1. Launch the app
2. Toggle "🎮 Demo Mode" ON in the sidebar
3. Enter any activity and see simulated results

## 📝 Usage

1. **Enter your activity** - Type what you want to do (typos OK!)
   - Examples: "washin my car", "gonna do sum gardning", "read a book"

2. **Set your location** - Enter your city in the sidebar

3. **Click Analyze** - Watch the magic happen!

4. **View Results:**
   - 📊 **SkyScore** - Your 0-100% recommendation
   - 🌡️ **Weather Card** - Current conditions
   - 🧠 **Analysis** - How AI understood your input
   - 📋 **Factors** - What affected your score
   - 🗺️ **Map** - Your location visualized

## 🎨 UI Features

- **Glassmorphism Design** - Frosted glass effect cards
- **Gradient Backgrounds** - Purple/blue color scheme
- **Animated Score Gauge** - Circular progress indicator
- **Weather Emojis** - Dynamic icons based on conditions
- **GSAP Animations** - Smooth entrance effects
- **Responsive Layout** - Works on all screen sizes

## 📁 Project Structure

```
Project Ai/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .env               # API keys (create this)
```

## ⚙️ Environment Variables (Optional)

Create a `.env` file:

```env
OPENAI_API_KEY=sk-your-key-here
OPENWEATHER_API_KEY=your-key-here
```

## 🔧 Configuration

All scoring parameters can be adjusted in the `Config` class:

```python
@dataclass
class Config:
    rain_threshold: float = 0.0       # mm
    wind_threshold_mph: float = 15.0  # mph
    heat_threshold_c: float = 30.0    # °C
    
    outdoor_rain_penalty: int = -80
    outdoor_wind_penalty: int = -30
    indoor_rain_bonus: int = 20
    indoor_heat_bonus: int = 10
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| AI/NLP | OpenAI GPT-4 |
| Weather API | OpenWeatherMap |
| Maps | Folium + streamlit-folium |
| Styling | Custom CSS + GSAP |
| Language | Python 3.9+ |

## 📜 License

MIT License - Feel free to use and modify!

---

<div align="center">

**Built with ❤️ using Streamlit & OpenAI**

🌤️ *Let the weather guide your day!*

</div>
