# Cartoon of the Day - UI Specification

## Overview
A web application that generates AI-powered cartoon concepts based on local news. Users provide their location, and the app creates a humorous cartoon inspired by today's local headlines.

## Core User Flow
1. User sets their location (via GPS detection or manual entry)
2. User clicks generate to create a cartoon based on local news
3. User views the generated cartoon with concept details

## Page Structure

### 1. Header Section
- **Title**: "🎨 Cartoon of the Day"
  - Large, bold font (3rem/48px)
  - Purple-to-pink gradient text
  - Centered alignment
- **Subtitle**: "AI-powered cartoons based on your local news"
  - Smaller, muted text (1.25rem/20px)
  - Gray color (#6b7280)

### 2. Progress Indicator
- **Design**: Simple 2-step horizontal progress bar
- **Steps**:
  1. "Set Location" - Shows number "1" or checkmark if complete
  2. "View Cartoon" - Shows number "2" or checkmark if complete
- **Visual states**:
  - Pending: Gray circle with number
  - Active: Purple border with purple background tint
  - Completed: Green checkmark
- **Connector**: Arrow between steps

### 3. Main Action Area

#### State A: No Location Set
- **Card container** with rounded corners and subtle shadow
- **Card title**: "🗞️ Get Your Daily Cartoon!"
- **Card subtitle**: "Tell us your location, and we'll generate a unique cartoon based on today's local news."
- **Two primary action buttons** (side by side):
  - Left: "📍 Detect My Location"
  - Right: "⌨️ Enter Location Manually"
- **Buttons styling**:
  - Large size (padding: 1rem 2rem)
  - Purple gradient background
  - White text
  - Rounded corners (12px radius)
  - Hover effect: Lift up 3px with shadow

#### State B: Manual Location Entry (after clicking manual button)
- **Quick suggestion buttons**:
  - 4 popular cities in a row (London, New York, Tokyo, Sydney)
  - Small, outline style buttons
- **Text input field**:
  - Placeholder: "e.g., Paris, France"
  - Large, rounded input (12px radius)
  - Purple focus border
- **Action buttons** (2 columns):
  - Left: "Cancel" (outline style)
  - Right: "Use This Location" (filled, primary style)

#### State C: Location Set
- **Success message**: Green alert bar showing "📍 Location set: [City, Country]"
- **Change button**: Small button to modify location
- **Primary action**: Large "✨ Generate Today's Cartoon" button
  - Full width
  - Purple gradient background
  - Prominent size and shadow

### 4. Generation Progress (while generating)
- **Progress bar**: 0-100% animated fill
- **Status messages** that update for each step:
  1. "📰 Finding today's local news..." (0-30%)
  2. "💭 Creating cartoon concepts..." (30-60%)
  3. "🎨 Drawing your cartoon..." (60-90%)
  4. "✅ Complete! Your cartoon is ready!" (100%)

### 5. Results Display

#### Cartoon Display Card
- **Topic banner**: Full-width purple gradient bar
  - Text: "📰 Today's Topic: [Topic Name]"
  - White text on gradient background
- **Two-column layout**:
  - **Left column**: Generated cartoon image
  - **Right column**:
    - Title: "🏆 [Winning Cartoon Title]"
    - Story/Premise text
    - "Why it's funny" explanation
    - Action buttons:
      - "💾 Download" - Downloads the image
      - "📋 Share" - Copies to clipboard

#### All Concepts Section
- **Expandable accordion**: "📊 See All Concepts"
- **When expanded**: List of 5 ranked concepts
  - Each shows: Rank number, title, premise, why funny
  - Winner marked with 🏆 emoji

### 6. Status Messages
- **Design**: Prominent alert bars with:
  - 4px colored left border
  - Icon on left (💡 info, ✅ success, ❌ error)
  - Message text
  - Tinted background matching status type
- **Types**:
  - Info (blue): Default helpful messages
  - Success (green): Successful operations
  - Error (red): Error messages

### 7. Footer
- Simple centered text with divider above
- "🤖 Powered by Google Gemini AI • ❤️ Made with Streamlit 🎨"

## Visual Design System

### Colors
- **Primary**: Purple #8b5cf6
- **Secondary**: Pink #ec4899
- **Success**: Green #10b981
- **Error**: Red #ef4444
- **Muted**: Gray #6b7280
- **Border**: Light gray #e5e7eb
- **Background**: White #ffffff
- **Gradient**: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)

### Typography
- **Hero title**: 3rem (48px), bold, gradient text
- **Section titles**: 1.5rem (24px), bold
- **Body text**: 1rem (16px), regular
- **Button text**: 1.1rem (17.6px), bold
- **Small text**: 0.875rem (14px)

### Spacing
- **Container max-width**: 900px
- **Section padding**: 2rem
- **Card padding**: 2rem
- **Button padding**: 1rem 2rem
- **Element gaps**: 1rem between related items

### Interactive Elements
- **Buttons**:
  - Primary: Purple gradient fill, white text
  - Secondary: Transparent with purple border
  - Hover: Translate up 3px, increase shadow
  - Active: Return to original position
- **Cards**:
  - White background (light mode)
  - 1px border (#e5e7eb)
  - 16px border radius
  - Subtle shadow (0 4px 6px rgba(0,0,0,0.05))
- **Input fields**:
  - 2px border
  - 12px border radius
  - Purple focus border with glow

### Animations
- **Fade in down**: Hero header entrance
- **Fade in up**: Cards and results entrance
- **Progress bar**: Smooth fill animation
- **Button hover**: Transform translateY(-3px)
- **Celebration**: Balloon animation on completion

## Mobile Responsiveness
- Single column layout on screens < 768px
- Full-width buttons on mobile
- Larger touch targets (min 44px)
- Simplified navigation
- Stack columns vertically

## State Management
The UI should track these states:
- `location`: User's selected location (null or {city, country})
- `isGenerating`: Whether cartoon generation is in progress
- `cartoon`: Generated cartoon data (null or object)
- `error`: Any error messages to display

## User Interactions

### Location Detection Flow
1. User clicks "Detect My Location"
2. Browser prompts for location permission
3. If granted: Get GPS → Reverse geocode → Show location
4. If denied: Show error → Suggest manual entry

### Manual Location Flow
1. User clicks "Enter Location Manually"
2. Can either:
   - Click a suggested city button
   - Type custom location and click "Use This Location"
3. Validate location exists
4. Show success message with location

### Generation Flow
1. User clicks "Generate Today's Cartoon"
2. Show progress bar with status updates
3. Fetch news → Generate concepts → Create image
4. Display results with celebration animation
5. Enable download and share options

## Accessibility Requirements
- All interactive elements keyboard accessible
- ARIA labels for icons
- Color contrast ratio ≥ 4.5:1
- Focus indicators visible
- Screen reader friendly status messages
- Alt text for cartoon images

## Error Handling
- Network errors: "❌ Connection error. Please check your internet and try again."
- Location not found: "❌ Could not find '[location]'. Please try a different location."
- Generation failure: "❌ Oops! Something went wrong. Please try again."
- API limits: "❌ Daily limit reached. Please try again tomorrow."

## Additional Features
- **Local Storage**: Save user's location preference
- **History**: Sidebar showing last 5 generated cartoons
- **Dark Mode**: Toggle between light and dark themes
- **Share**: Copy cartoon text or download image
- **Loading States**: Skeleton screens while loading