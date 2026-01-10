# Project Context Rules

This project has two technical contexts:

1. Backend (NestJS + Prisma)
   - Rules live in `backend/rules.md`
   - If a task mentions:
     - API
     - endpoint
     - database
     - prisma
     - service
     - module
     → apply backend rules by default.

2. Frontend (React + Vite + TS + Tailwind)
   - Rules live in `frontend/rules.md`
   - If a task mentions:
     - UI
     - component
     - page
     - Tailwind
     - React
     → apply frontend rules by default.

If a task is ambiguous:
- Ask for clarification before generating code.



# proyect.md — Anime Season Tracker (Web App)
Stack: React + Vite + TypeScript + Tailwind | NestJS | PostgreSQL | Prisma  
Deploy (free): Front (Vercel/Netlify) | API (Render) | DB (Neon/Supabase)

---

## Objetivo del producto (MVP)
Una webapp que:
1) Lista **todos** los animes de una temporada (Winter/Spring/Summer/Fall + año) desde AniList.
2) Permite al usuario **seguir** animes (watchlist).
3) Muestra **noticias** (ANN + Crunchy) con deduplicación.
4) Se puede usar desde un host gratuito (deploy temprano).

---

## Reglas de alcance (para ir rápido)
- No microservicios.
- No SSR/Next.
- No login complejo en MVP (watchlist anónimo o user simple).
- No colas/Redis en MVP.
- Datos “source of truth” de temporadas: AniList GraphQL.
- Noticias: RSS si existe; scraping solo si no hay feed estable.

---
## Etapas y entregables (con commits)


## antes de comenzar crear

estructura del repo

Anime_Tracker_App/
├─ backend/
│  ├─ src/
│  │  ├─ modules/
│  │  │  ├─ catalog/
│  │  │  ├─ news/
│  │  │  ├─ watchlist/
│  │  ├─ app.module.ts
│  │  └─ main.ts
│  ├─ prisma/
│  │  └─ schema.prisma
│  └─ Dockerfile
├─ frontend/
│  ├─ src/
│  ├─ tailwind.config.ts
│  └─ vite.config.ts
├─ docker-compose.yml


### Stage 0 — Repository Bootstrap (0.5 day)
**Deliverables**
- Monorepo created.
- Frontend and backend running locally.
- Basic standards in place (lint/format optional).

**Commits**
- `chore: init monorepo structure (frontend/backend)`
- `feat(web): bootstrap react (vite + ts)`
- `feat(api): bootstrap nestjs project`
- `docs: add initial README (setup + scripts)`

---

### Stage 1 — Local Infrastructure (DB + Prisma) (0.5–1 day)
**Deliverables**
- Local PostgreSQL via Docker.
- Prisma initialized.
- First migration applied.

**Commits**
- `chore(db): add postgres docker compose`
- `chore(db): init prisma + database connection`
- `chore(db): add initial migration`

**Minimum Models (Prisma)**
- Anime (external IDs, titles, cover image)
- SeasonEntry (year, season, animeId)
- NewsItem (source, unique url, title, publishedAt, hash)
- WatchlistItem (clientId/userId, animeId)

---

### Stage 2 — Seasonal Catalog (AniList) (1–2 days)
**Deliverables**
- Endpoint: `GET /api/seasons/:year/:season`
- Normalized response (your own DTO).
- Persistent cache (store SeasonEntry + Anime in DB).
- Basic rate limiting by design (cache + pagination).

**Commits**
- `feat(api): add catalog module skeleton`
- `feat(api): add anilist client (graphql)`
- `feat(api): implement season fetch + pagination`
- `feat(api): persist season catalog (anime + season entries)`
- `feat(api): expose seasons endpoint (GET /api/seasons/:year/:season)`

**Notes**
- `season`: `winter|spring|summer|fall`
- Store `anilistId` and titles (romaji/english/native) + image.
- MVP cache policy: if the season exists in DB and was updated within X hours, return DB data.

---

### Stage 3 — Season Frontend (1 day)
**Deliverables**
- Main screen:
  - Year + season selector
  - Anime list (cards)
  - Basic filters (text search)
- Real consumption of the backend endpoint.

**Commits**
- `feat(web): add layout + routing`
- `feat(web): season selector + season page`
- `feat(web): integrate seasons api + loading/error states`
- `ui: add anime card component + basic filters`

---

### Stage 4 — Watchlist (0.5–1 day)
**Deliverables**
- Functional watchlist without login:
  - `clientId` generated and stored in localStorage
- Endpoints:
  - `GET /api/watchlist`
  - `POST /api/watchlist/:animeId`
  - `DELETE /api/watchlist/:animeId`
- UI: “Follow” / “Unfollow” button and watchlist page.

**Commits**
- `feat(api): add watchlist module + endpoints`
- `feat(api): persist watchlist items (clientId + animeId)`
- `feat(web): add watchlist actions (follow/unfollow)`
- `feat(web): add watchlist page`

---

### Stage 5 — News (ANN + Crunchy) (1–2 days)
**Deliverables**
- Ingestor per source:
  - Prefer RSS/Atom when available.
  - If no stable feed exists, controlled scraping (single route per source).
- Deduplication:
  - Unique `url`
  - `hash(title + publishedAt + source)`
- Endpoint:
  - `GET /api/news?source=ann|crunchy&limit=...`
- UI:
  - list with source filters
  - external article link

**Commits**
- `feat(api): add news module skeleton`
- `feat(api): impl
