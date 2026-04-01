# SkyCoach AI - React Frontend

Modern React 18 + TypeScript + Vite frontend for the SkyCoach AI weather-based activity advisor.

## Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Features

- **Modern UI**: Built with React, TypeScript, and TailwindCSS
- **Glassmorphism Design**: Consistent with backend styling
- **Real-time Analysis**: Connect to FastAPI backend for activity scoring
- **Auto-Judge**: Shows intelligent suggestions for incomplete inputs
- **Weather Integration**: Displays current weather conditions
- **Responsive Design**: Mobile-friendly interface
- **Performance**: Vite for fast builds and HMR

## Architecture

```
src/
├── components/        # React components
│   ├── ActivityInput.tsx      # Input form for activity & location
│   ├── AnalysisResult.tsx     # Main results container
│   ├── TaskCard.tsx           # Activity analysis display
│   ├── WeatherCard.tsx        # Weather information
│   ├── ScoreCard.tsx          # SkyScore visualization
│   ├── AlternativesCard.tsx   # Alternative suggestions
│   └── Header.tsx             # App header
├── pages/            # Page components
│   └── Dashboard.tsx          # Main dashboard page
├── services/         # API integration
│   └── api.ts                 # Backend API client
├── hooks/           # Custom React hooks
│   └── useApi.ts              # API hooks with React Query
├── types/           # TypeScript type definitions
│   └── api.ts                 # API response types
├── styles/          # CSS stylesheets
│   └── globals.css            # Global styles & animations
├── utils/           # Utility functions
├── App.tsx          # Root component
└── main.tsx         # Entry point
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=SkyCoach AI
```

### API Connection

The frontend automatically connects to the FastAPI backend via proxy (Vite dev server).

To change the backend URL, modify `vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',  // Change this
    changeOrigin: true,
  },
}
```

## Development

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Linting

```bash
npm run lint
```

### Format Code

```bash
npm run format
```

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **TailwindCSS** - Utility-first CSS
- **React Query** - State management & caching
- **Axios** - HTTP client
- **GSAP** - Animation library
- **Lucide React** - Icon library

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Project Structure Highlights

### Components

Each component is self-contained with its own styling and logic:

- **ActivityInput**: Form for entering activity and location
- **TaskCard**: Displays task analysis with auto-judge suggestions
- **WeatherCard**: Shows current weather conditions
- **ScoreCard**: Visualizes SkyScore with factors
- **AlternativesCard**: Lists alternative activity suggestions

### State Management

Uses React Query for:

- Caching API responses
- Managing async states (loading, error, success)
- Background synchronization
- Stale time management

### Styling

- **TailwindCSS** for responsive design
- **Custom CSS** for animations and glassmorphism effects
- **CSS-in-JS** support via Tailwind utilities

## API Integration

The frontend connects to these backend endpoints:

- `POST /api/analyze-task` - Analyze an activity
- `POST /api/weather` - Get weather data
- `POST /api/analyze` - Full end-to-end analysis
- `GET /api/alternatives` - Get alternative activities
- `GET /api/health` - Health check

## Troubleshooting

### API Connection Error

Ensure the backend is running:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Port Already in Use

Change the port in `vite.config.ts`:

```typescript
server: {
  port: 3001,  // Change this
}
```

### Module Import Errors

Make sure path aliases in `tsconfig.json` match your actual directory structure.

## Next Steps

1. Implement actual component styling and animations
2. Add WebSocket support for real-time updates
3. Integrate GSAP animations
4. Add local storage for history
5. Implement authentication
6. Deploy to production

## License

Part of SkyCoach AI project
