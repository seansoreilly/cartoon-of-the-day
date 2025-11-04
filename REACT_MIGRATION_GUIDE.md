# React + shadcn/ui Migration Guide

## Difficulty Assessment: **Medium** (3/5)

The migration is very feasible because:
- ✅ Clear separation of concerns already exists (location, news, cartoon generation)
- ✅ UI components map directly to shadcn/ui components
- ✅ State management is straightforward (just location, cartoon data, etc.)
- ✅ Already using modern UI patterns (cards, buttons, progress)

## Architecture Changes

### Current (Streamlit)
```
app.py (Everything)
├── UI Rendering
├── State Management
├── API Calls
└── Business Logic
```

### Target (React + FastAPI)
```
Frontend (React)          Backend (FastAPI)
├── Components           ├── /api/location
├── Pages                ├── /api/news
├── State (Zustand)      ├── /api/cartoon
└── API Client           └── /api/image
```

## Component Mapping

| Current (Streamlit) | React + shadcn/ui |
|-------------------|------------------|
| `st.button()` | `<Button />` |
| `st.columns()` | `<div className="grid grid-cols-2">` |
| Action Card | `<Card />` with `<CardHeader />`, `<CardContent />` |
| Progress Bar | `<Progress />` or custom stepper |
| Status Message | `<Alert />` |
| `st.spinner()` | `<Loader2 className="animate-spin" />` |
| `st.text_input()` | `<Input />` |
| `st.expander()` | `<Accordion />` |
| Modal/Dialog | `<Dialog />` |
| Toast | `<Toast />` using `useToast()` |

## React Component Structure

```typescript
// src/components/CartoonGenerator.tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import { MapPin, Sparkles, AlertCircle } from "lucide-react"

export function CartoonGenerator() {
  const [location, setLocation] = useState<Location | null>(null)
  const [cartoon, setCartoon] = useState<Cartoon | null>(null)
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState<'location' | 'cartoon'>('location')

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Hero Header */}
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          🎨 Cartoon of the Day
        </h1>
        <p className="text-muted-foreground text-lg mt-2">
          AI-powered cartoons based on your local news
        </p>
      </div>

      {/* Progress Steps */}
      <div className="flex justify-center items-center gap-4 mb-8">
        <Step number={1} label="Set Location" active={!location} completed={!!location} />
        <ArrowRight className="text-muted-foreground" />
        <Step number={2} label="View Cartoon" active={!!location} completed={!!cartoon} />
      </div>

      {/* Main Action Card */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-2xl text-center">
            🗞️ Get Your Daily Cartoon!
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!location ? (
            <LocationSelector onLocationSet={setLocation} />
          ) : (
            <GenerateSection location={location} onGenerate={handleGenerate} />
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {cartoon && <CartoonDisplay cartoon={cartoon} />}
    </div>
  )
}
```

## Key React Components to Build

### 1. LocationSelector Component
```typescript
function LocationSelector({ onLocationSet }: { onLocationSet: (loc: Location) => void }) {
  const [mode, setMode] = useState<'choice' | 'detect' | 'manual'>('choice')

  if (mode === 'choice') {
    return (
      <div className="grid grid-cols-2 gap-4">
        <Button size="lg" onClick={() => setMode('detect')}>
          <MapPin className="mr-2" /> Detect My Location
        </Button>
        <Button size="lg" variant="outline" onClick={() => setMode('manual')}>
          <Keyboard className="mr-2" /> Enter Manually
        </Button>
      </div>
    )
  }

  // Handle detect and manual modes...
}
```

### 2. API Service Layer
```typescript
// src/services/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = {
  async detectLocation(): Promise<Location> {
    const res = await fetch(`${API_BASE}/api/location/detect`)
    return res.json()
  },

  async generateCartoon(location: Location): Promise<Cartoon> {
    const res = await fetch(`${API_BASE}/api/cartoon/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ location })
    })
    return res.json()
  }
}
```

### 3. State Management with Zustand
```typescript
// src/store/cartoon-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface CartoonStore {
  location: Location | null
  cartoon: Cartoon | null
  history: Cartoon[]
  setLocation: (location: Location) => void
  setCartoon: (cartoon: Cartoon) => void
  addToHistory: (cartoon: Cartoon) => void
  reset: () => void
}

export const useCartoonStore = create<CartoonStore>()(
  persist(
    (set) => ({
      location: null,
      cartoon: null,
      history: [],
      setLocation: (location) => set({ location }),
      setCartoon: (cartoon) => set({ cartoon }),
      addToHistory: (cartoon) => set((state) => ({
        history: [cartoon, ...state.history].slice(0, 10)
      })),
      reset: () => set({ location: null, cartoon: null })
    }),
    {
      name: 'cartoon-storage'
    }
  )
)
```

## FastAPI Backend

```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from src.location_detector import LocationDetector
from src.news_fetcher import NewsFetcher
from src.cartoon_generator import CartoonGenerator
from src.image_generator import ImageGenerator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LocationRequest(BaseModel):
    query: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@app.post("/api/location/detect")
async def detect_location(request: LocationRequest):
    detector = LocationDetector()
    result = detector.get_location_with_fallback(request.query)
    if not result:
        raise HTTPException(status_code=404, detail="Location not found")
    coords, address = result
    return {"coords": coords, "address": address}

@app.post("/api/cartoon/generate")
async def generate_cartoon(location: dict):
    # Fetch news
    fetcher = NewsFetcher()
    news_result = fetcher.fetch_and_summarize(
        location['address']['city'],
        location['address']['country']
    )

    # Generate cartoon
    generator = CartoonGenerator()
    cartoon_data = generator.generate_concepts(
        news_result['dominant_topic'],
        f"{location['address']['city']}, {location['address']['country']}",
        news_result['summary']
    )

    # Generate image
    image_gen = ImageGenerator()
    image_path = image_gen.generate_and_save(cartoon_data)

    return {
        "cartoon": cartoon_data,
        "image_url": f"/api/image/{image_path.name}",
        "news": news_result
    }

@app.get("/api/image/{filename}")
async def get_image(filename: str):
    # Serve generated images
    return FileResponse(f"data/cartoons/{filename}")
```

## shadcn/ui Setup

```bash
# Initialize Next.js with TypeScript
npx create-next-app@latest cartoon-app --typescript --tailwind --app

cd cartoon-app

# Install shadcn/ui
npx shadcn-ui@latest init

# Add components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add alert
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add input
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add accordion

# Additional dependencies
npm install zustand lucide-react framer-motion
```

## Migration Steps

### Phase 1: Backend API (2-3 hours)
1. Create FastAPI project structure
2. Move Python logic to API endpoints
3. Add CORS support
4. Test endpoints with Postman/Thunder Client

### Phase 2: React Setup (1 hour)
1. Initialize Next.js project
2. Install shadcn/ui and configure
3. Set up project structure
4. Configure environment variables

### Phase 3: Core Components (3-4 hours)
1. Build LocationSelector component
2. Build CartoonGenerator component
3. Build CartoonDisplay component
4. Implement progress stepper

### Phase 4: State & API Integration (2-3 hours)
1. Set up Zustand store
2. Create API service layer
3. Connect components to API
4. Handle loading states

### Phase 5: Polish (2-3 hours)
1. Add animations with Framer Motion
2. Implement error boundaries
3. Add toast notifications
4. Mobile responsiveness
5. Dark mode support

## Total Estimated Time: 10-14 hours

## Advantages of React + shadcn/ui

### Performance
- Client-side rendering = faster interactions
- Image lazy loading
- Code splitting
- Better caching strategies

### Developer Experience
- TypeScript for type safety
- Component reusability
- Better debugging with React DevTools
- Hot module replacement

### User Experience
- Instant feedback (no page reloads)
- Smooth animations
- Offline capability with PWA
- Better mobile experience

### Deployment
- Static hosting on Vercel/Netlify (frontend)
- Serverless functions or containerized API (backend)
- CDN for assets
- Easier scaling

## Example shadcn/ui Components

### Alert Component (Status Messages)
```tsx
<Alert className="mb-4">
  <AlertCircle className="h-4 w-4" />
  <AlertTitle>Location Detected</AlertTitle>
  <AlertDescription>
    📍 Melbourne, Australia - Ready to generate your cartoon!
  </AlertDescription>
</Alert>
```

### Progress Component
```tsx
<Progress value={progressValue} className="w-full" />
```

### Custom Stepper Component
```tsx
const Step = ({ number, label, active, completed }) => (
  <div className={cn(
    "flex items-center gap-2 px-4 py-2 rounded-full",
    "border-2 transition-all",
    active && "border-purple-600 bg-purple-50",
    completed && "border-green-600 bg-green-50"
  )}>
    <div className={cn(
      "w-8 h-8 rounded-full flex items-center justify-center",
      "font-bold text-white",
      completed ? "bg-green-600" : "bg-gradient-to-r from-purple-600 to-pink-600"
    )}>
      {completed ? "✓" : number}
    </div>
    <span className="font-medium">{label}</span>
  </div>
)
```

## Conclusion

The migration to React + shadcn/ui is very feasible and would provide:
- Better performance
- More maintainable codebase
- Modern development experience
- Better user experience
- Easier deployment and scaling

The main effort is in:
1. Setting up the backend API (FastAPI)
2. Building the React components
3. Connecting everything together

With shadcn/ui, you get beautiful, accessible components out of the box that match your current design aesthetic perfectly.