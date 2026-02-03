# Frontend - Seasonal Anime Tracker

Next.js TypeScript frontend for the Seasonal Anime Tracker application.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Package Manager**: pnpm

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Home page
│   ├── globals.css             # Global styles
│   ├── providers/
│   │   └── QueryProvider.tsx   # TanStack Query setup
│   └── types/
│       └── anime.ts            # TypeScript interfaces
├── next.config.mjs             # Next.js configuration
├── tailwind.config.ts          # Tailwind CSS configuration
└── tsconfig.json               # TypeScript configuration

```

## Getting Started

### Prerequisites

- Node.js 20+
- pnpm 9+

### Installation

```bash
# Install dependencies
pnpm install
```

### Development

```bash
# Start development server
pnpm dev
```

The application will be available at `http://localhost:3000`

### Build

```bash
# Build for production
pnpm build

# Start production server
pnpm start
```

## Configuration

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Features Implemented

### Task 5.1: Next.js Project Structure ✅
- Next.js 14 with App Router
- TypeScript configuration
- Tailwind CSS setup
- TanStack Query integration

### Task 5.2: TypeScript Interfaces ✅
- Comprehensive anime data types
- API error interfaces
- Component props types
- Matches backend Pydantic models

### Task 5.3: TanStack Query Provider ✅
- Stale-while-revalidate caching (5-minute stale time)
- Exponential backoff retry logic
- Background refetch on window focus
- Optimized query configuration

## Next Steps

The frontend foundation is complete. Next tasks include:
- API client service implementation
- UI components (AnimeCard, AnimeGrid, LoadingSkeleton)
- Data fetching hooks
- Error handling and toast notifications

## Development Guidelines

- Follow the TypeScript guidelines in `frontend.md`
- Use absolute imports with `@/` prefix
- Keep components focused and single-purpose
- Write tests for all new features
- Ensure responsive design across all screen sizes
