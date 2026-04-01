# React Frontend Architecture & Setup

## Project Structure

```
frontend/
├── src/
│   ├── components/           # React UI components
│   │   ├── ActivityInput.tsx
│   │   ├── AnalysisResult.tsx
│   │   ├── TaskCard.tsx
│   │   ├── WeatherCard.tsx
│   │   ├── ScoreCard.tsx
│   │   ├── AlternativesCard.tsx
│   │   ├── Header.tsx
│   │   └── index.ts
│   ├── pages/
│   │   └── Dashboard.tsx      # Main dashboard page
│   ├── services/
│   │   └── api.ts            # Axios API client
│   ├── hooks/
│   │   └── useApi.ts         # React Query hooks
│   ├── types/
│   │   └── api.ts            # TypeScript interfaces
│   ├── styles/
│   │   └── globals.css       # Global styling
│   ├── utils/                # Utility functions
│   ├── App.tsx               # Root component
│   └── main.tsx              # Vite entry point
├── public/                    # Static assets
├── index.html                 # HTML template
├── package.json               # Dependencies
├── tsconfig.json              # TypeScript config
├── tsconfig.node.json         # Vite TypeScript config
├── vite.config.ts             # Vite configuration
├── tailwind.config.js         # TailwindCSS config
├── postcss.config.js          # PostCSS config
├── .env                       # Environment variables
├── .env.example               # Example env file
├── .gitignore                 # Git ignore rules
└── README.md                  # Documentation
```

## Technology Stack

### Core Framework

- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Modern build tool (HMR, fast builds)

### State & Data

- **React Query** - Server state, caching, sync
- **Axios** - HTTP client with interceptors

### Styling

- **TailwindCSS** - Utility-first CSS
- **PostCSS/Autoprefixer** - CSS processing
- **Custom CSS** - Animations & glassmorphism

### Additional

- **GSAP** - Advanced animations
- **Lucide React** - Icon library

## Key Features

### 1. **Component Architecture**

Modular, single-responsibility components:

```
ActivityInput (form)
    ↓
Dashboard (orchestrator)
    ↓ (onAnalyze callback)
useFullAnalysis hook (API call)
    ↓
AnalysisResult (container)
    ├── TaskCard (activity analysis)
    ├── WeatherCard (weather data)
    ├── ScoreCard (SkyScore + factors)
    └── AlternativesCard (suggestions)
```

### 2. **API Integration**

Type-safe API client with React Query hooks:

```typescript
// Basic API call
const { mutate: runAnalysis, isLoading } = useFullAnalysis();
runAnalysis(
  { activity, city },
  {
    onSuccess: (data) => setAnalysis(data),
    onError: (error) => console.error(error),
  },
);

// Automatic caching, retry, stale time management
```

### 3. **State Management**

Uses React Query for:

- Automatic caching of API responses
- Background data refetching
- Loading/error states
- Stale data management

No Redux/Zustand needed for this use case.

### 4. **Styling System**

**TailwindCSS** with custom utilities:

```css
/* Glassmorphism */
.glass {
  background: rgba(10, 15, 30, 0.48);
  backdrop-filter: blur(32px);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

/* Animations */
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
.animate-slide-in-left {
  animation: slideInFromLeft 0.5s ease-out;
}
```

### 5. **Responsive Design**

Mobile-first breakpoints:

- `sm: 640px` - Tablet
- `md: 768px` - Desktop
- `lg: 1024px` - Large desktop

```html
<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
  <!-- Stacks on mobile, 3 columns on large screens -->
</div>
```

## Development Workflow

### Setup

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:3000` with hot reload.

### Build

```bash
npm run build
npm run preview
```

Generates optimized production build in `dist/`.

### Type Checking

Full TypeScript compilation:

- Component props are type-safe
- API responses are validated at type level
- IDE autocomplete for all APIs

## API Integration Grid

| Endpoint        | Method | Purpose                | Hook                   |
| --------------- | ------ | ---------------------- | ---------------------- |
| `/analyze-task` | POST   | Analyze activity text  | `useAnalyzeTask()`     |
| `/weather`      | POST   | Fetch weather data     | `useGetWeather()`      |
| `/analyze`      | POST   | Full pipeline          | `useFullAnalysis()`    |
| `/alternatives` | GET    | Alternative activities | `useGetAlternatives()` |
| `/health`       | GET    | Backend health check   | Direct call            |

## Component Details

### ActivityInput

- Form with textarea for activity description
- Text input for city/location
- Submit button with loading state
- Input validation

### TaskCard

- Displays original input and cleaned text
- Shows classification (Indoor/Outdoor)
- Confidence score with progress bar
- Auto-judge suggestion section (if available)

### WeatherCard

- Temperature with feels-like
- Condition with emoji
- Humidity, wind speed, precipitation
- Coordinates display
- Grid layout for responsive display

### ScoreCard

- Large circular score display (0-100)
- Color-coded: Green/Cyan/Yellow/Red
- Label based on score (Perfect/Go/Possible/Not ideal)
- Bonuses and penalties breakdown
- Recommendation text
- Weather factors list

### AlternativesCard

- Grid of alternative activity suggestions
- Hover effects
- Classification label
- Reason explanation

## Performance Optimizations

1. **Code Splitting**: Vite automatically chunks dependencies
2. **Image Optimization**: Using SVG icons
3. **Lazy Suspense**: Components can use React.lazy()
4. **Query Caching**: React Query caches results by default
5. **Memoization**: Can use React.memo() for heavy components

## Testing Setup (Optional)

For future implementation:

```bash
npm install --save-dev vitest @testing-library/react
```

## Environment Configuration

Change backend URL without rebuilding:

```env
# .env
VITE_API_URL=http://api.example.com
```

Vite also auto-proxies `/api` to backend in dev mode.

## Browser Support

- Modern browsers (ES2020+)
- Chrome, Firefox, Safari, Edge (latest versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Security Considerations

- CORS configured in FastAPI backend
- Environment variables for sensitive data
- No hardcoded API keys in frontend
- Axios request/response interceptors ready for auth tokens

## Next Steps for Task #14

After this structure is set up:

1. Implement GSAP animations in components
2. Add WebSocket support for real-time updates
3. Create custom hooks for complex logic
4. Add unit tests with Vitest
5. Implement error boundaries
6. Add loading skeletons

## File Locations Reference

- **Types**: `src/types/api.ts` - Update when backend schema changes
- **API Calls**: `src/services/api.ts` - Update with new endpoints
- **Styles**: `src/styles/globals.css` - Theme colors defined here
- **Components**: `src/components/*.tsx` - Add new components here
- **Config**: Files in root (`vite.config.ts`, `tailwind.config.js`, etc.)
