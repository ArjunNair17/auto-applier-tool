# Auto-Applier v2 - Desktop Application

A full-featured desktop application that wraps the existing CLI automation (v1) in a graphical interface.

## Architecture

```
┌──────────────── Tauri (Rust) ────────────────┐
│  WebView ← React UI                           │
│     ↑ HTTP/WS                                 │
│  Sidecar: spawns & supervises Python          │
└───────────────────┬───────────────────────────┘
                    │ localhost:PORT
        ┌───────────▼────────────┐
        │  FastAPI backend       │
        │  ├─ REST: CRUD         │
        │  ├─ WS:  live events   │
        │  └─ RunWorker (asyncio)│
        │       ├─ Playwright    │
        │       └─ ats_handlers/ │ ← imports v1 modules
        └───────────┬────────────┘
                    │
              SQLite (~/Library/Application Support/AutoApplier/v2.db)
```

## Development

### Prerequisites

1. **Python 3.11+**
   - pip install -r backend/pyproject.toml

2. **Node.js 18+**
   - npm install (in app/frontend/)

3. **Rust (via rustup)**
   - curl --proto '=https' --silent --location https://sh.rustup.rs | sh
   - rustup default stable

### Running the Development Environment

```bash
cd app
./scripts/dev.sh
```

This will start:
- FastAPI backend on http://localhost:8000 (or random port)
- Vite frontend on http://localhost:5173
- Tauri development window

All three run concurrently.

## Project Structure

```
app/
├── backend/                 # Python FastAPI sidecar
│   ├── auto_applier_api/
│   │   ├── api/           # REST endpoints
│   │   ├── db/            # SQLAlchemy models, migrations
│   │   ├── core/          # Run worker, ATS adapter
│   │   └── services/      # Business logic
│   ├── pyproject.toml
│   └── tests/
│
├── frontend/                # React + Vite
│   ├── src/
│   │   ├── routes/       # Dashboard, Jobs, Run, History, Profile, Settings
│   │   ├── components/    # UI components
│   │   ├── lib/          # API client, WebSocket client, stores
│   │   └── store/        # Zustand state management
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
│
├── tauri/                   # Rust shell
│   ├── src/
│   │   ├── main.rs      # Tauri commands
│   │   └── sidecar.rs   # Backend process management
│   ├── Cargo.toml
│   └── tauri.conf.json
│
└── scripts/
    ├── dev.sh               # Concurrent development runner
    └── package.sh           # Production bundler
```

## Current Status

### ✅ Completed (Phase 0)
- Backend scaffold with FastAPI
- Frontend scaffold with React + TypeScript + Vite
- Tauri shell scaffolding
- Development script for running all three concurrently

### 🚧 In Progress
- Backend Core (SQLAlchemy models, repository layer, ATS adapter)
- Frontend Shell (routing, shadcn/ui setup)

### 📋 Planned
- Full API implementation
- WebSocket event streaming
- Run worker with v1 integration
- Complete UI views (Dashboard, Jobs, Run, History, Profile, Settings)
- Testing and CI/CD
- macOS packaging

## v1 vs v2

### v1 (CLI)
- **Location**: `../` (repo root)
- **Interface**: Command line
- **Database**: CSV files
- **Automation**: Direct Python script execution
- **Use when**: Quick, scriptable, or running in CI

### v2 (Desktop App)
- **Location**: `app/` (parallel to v1)
- **Interface**: Graphical desktop application
- **Database**: SQLite via SQLAlchemy 2.0
- **Automation**: Python FastAPI sidecar with WebSocket events
- **Use when**: Full control needed, real-time feedback required, running many jobs

Both versions can be used independently. v2 does not modify v1 code.
