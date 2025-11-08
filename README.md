# Cartoon of the Day - React TypeScript Edition

A modern React application that generates AI-powered cartoon concepts based on local news using Google News and Gemini AI.

## Features

- **Location Detection**: GPS-based location detection with manual entry and IP fallback
- **Local News Fetching**: Real-time local news from Google News
- **AI-Powered Concepts**: Generate cartoon concepts using Gemini AI
- **Image Generation**: Create cartoon images in newspaper cartoon style
- **History & Preferences**: Save generated cartoons and customize settings
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Performance Optimized**: Code splitting and component memoization for fast load times

## Tech Stack

- **Frontend Framework**: React 19 with TypeScript
- **Styling**: Tailwind CSS with custom configuration
- **State Management**: Zustand
- **Routing**: React Router v7
- **Build Tool**: Vite
- **Testing**: Vitest + React Testing Library
- **AI Services**: Google Gemini API

## Project Structure

```
cartoon-react/
├── src/
│   ├── components/        # React components
│   │   ├── cartoon/      # Cartoon-related components
│   │   ├── common/       # Shared components
│   │   ├── layout/       # Layout components
│   │   ├── location/     # Location detection components
│   │   └── news/         # News display components
│   ├── pages/            # Page components
│   ├── services/         # API and utility services
│   ├── store/            # Zustand stores
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
├── dist/                 # Production build output
├── public/               # Static assets
├── package.json          # Project dependencies
├── vite.config.ts        # Vite configuration
├── tsconfig.json         # TypeScript configuration
├── tailwind.config.ts    # Tailwind CSS configuration
├── netlify.toml          # Netlify deployment config
├── vercel.json           # Vercel deployment config
└── README.md            # This file
```

## Getting Started

### Prerequisites

- Node.js 20+ and npm 10+
- Google Gemini API key (get from https://aistudio.google.com/)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cartoon-of-the-day.git
cd cartoon-of-the-day/cartoon-react
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file with your API key:
```bash
cp .env.example .env.local
# Edit .env.local and add your VITE_GEMINI_API_KEY
```

4. Start the development server:
```bash
npm run dev
```

The application will open at http://localhost:5173

## Available Scripts

```bash
# Development
npm run dev          # Start Vite dev server
npm run preview      # Preview production build locally

# Building
npm run build        # Build for production

# Testing
npm test            # Run tests in watch mode
npm run test:ui     # Run tests with UI
npm run test:coverage  # Generate coverage report

# Quality
npm run lint        # Run ESLint
```

## Application Workflow

1. **Set Location**: Use GPS, manual entry, or IP-based detection
2. **View Local News**: See news articles relevant to your location
3. **Select Articles**: Choose news stories to generate cartoons from
4. **Generate Concepts**: AI generates multiple cartoon concept variations
5. **View Concepts**: See detailed descriptions and reasoning
6. **Generate Image**: Create an image based on the selected concept
7. **Download/Save**: Save the cartoon or share it

## Configuration

### Environment Variables

- `VITE_GEMINI_API_KEY`: Your Google Gemini API key (required)
- `VITE_API_BASE_URL`: Base URL for backend API (optional)
- `VITE_ENV`: Environment (development/production)

## Performance Features

- **Code Splitting**: Pages are lazy-loaded with React.lazy and Suspense
- **React.memo**: Expensive components are memoized to prevent unnecessary re-renders
- **Component Chunking**: Separate bundles for each page route
- **Optimized Assets**: CSS and JS minification with Vite

## Deployment

### Netlify

Already configured in `netlify.toml`. Connect your GitHub repository directly to Netlify for automatic deployments.

### Vercel

Already configured in `vercel.json`. Connect your GitHub repository directly to Vercel for automatic deployments.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Known Limitations

- Rate limited to 2 cartoon generations per minute per session
- News articles are limited to English language sources
- Image generation requires valid Google Gemini API key

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
