# Anime Season Tracker

A modern full-stack web application for tracking seasonal anime releases, built with FastAPI backend and React frontend.

## Architecture

- **Backend**: FastAPI (Python) with async support
- **Frontend**: React with Vite and TypeScript  
- **Data Source**: Jikan API (MyAnimeList)
- **Styling**: Tailwind CSS with Glassmorphism design
- **Caching**: In-memory cache with TTL support

## Prerequisites
- Python 3.8+ (for FastAPI backend)
- Node.js 20+ (for React frontend)
- pnpm 9+
- Docker (optional, for containerized deployment)

## Install
```bash
# Install all dependencies
pnpm install

# Install Python dependencies for backend
pnpm -C backend install
```

## Run
Backend (FastAPI):
```bash
pnpm dev:backend
```

Frontend (React + Vite):
```bash
pnpm dev:frontend
```

## Build
```bash
pnpm build
```

## Lint + Format
```bash
pnpm lint
pnpm format
```

## API Documentation

When running in development mode, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **httpx**: Async HTTP client for external API calls
- **uvicorn**: ASGI server for running FastAPI

### Frontend  
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **TanStack Query**: Data fetching and caching library
