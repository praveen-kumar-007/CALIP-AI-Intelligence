# CALIP &mdash; React Frontend Architecture

A modern, modular, component-driven React application designed for the **Cognitive Atomic Legal Intelligence Platform (CALIP)**.

---

## 🏛️ Architecture Overview

The frontend is decoupled from the backend and organized for maintainability, ease of change, and simple debugging.

```
frontend/
├── index.html                  # HTML entry point with Google Fonts (Plus Jakarta Sans, JetBrains Mono)
├── vite.config.js              # Vite bundler configuration + FastAPI API proxy setup
├── package.json                # React 18, React Router 6, Lucide Icons
└── src/
    ├── main.jsx                # React DOM root render
    ├── App.jsx                 # Client-side routing table (React Router v6)
    ├── index.css               # Design system tokens, glassmorphism, responsive grid & animations
    │
    ├── context/
    │   └── AppContext.jsx      # Global context: platform stats, health, and dynamic toast alerts
    │
    ├── services/
    │   └── api.js              # Centralized, typed API client matching all FastAPI endpoints
    │                           # Contains DEBUG_API logger toggle for quick console debugging
    │
    ├── components/
    │   ├── common/
    │   │   ├── Navbar.jsx      # Header with navigation links, live FastAPI status, and mobile drawer
    │   │   ├── Footer.jsx      # Open Data, LLM endpoints, and provenance footer
    │   │   ├── StatusBadge.jsx # Uniform badges for OCR status, court types, and case stages
    │   │   ├── LoadingSpinner.jsx # Clean SVG spinners and skeleton loading states
    │   │   └── Toast.jsx       # Floating notification alert system
    │   │
    │   ├── layout/
    │   │   └── MainLayout.jsx  # Main SPA shell
    │   │
    │   ├── search/
    │   │   └── SearchBar.jsx   # Search bar with Hybrid AI, Semantic Vector, and Keyword toggles
    │   │
    │   ├── cases/
    │   │   └── CaseCard.jsx    # Card rendering for court cases & dockets
    │   │
    │   ├── documents/
    │   │   └── DocumentCard.jsx# Card rendering for legal PDFs and OCR status
    │   │
    │   └── atoms/
    │       └── AtomCard.jsx    # Card rendering for 25-Layer Canonical FIR Atoms
    │
    └── pages/
        ├── HomePage.jsx        # Landing page with hero search, platform metrics, and flagship pillars
        ├── SearchPage.jsx      # Legal search results with scores and snippet highlights
        ├── CasesPage.jsx       # Filterable court cases directory
        ├── CaseDetailPage.jsx  # Dossier with facts, attached orders, and knowledge graph linkages
        ├── DocumentsPage.jsx   # Document archives with PDF upload modal
        ├── DocumentDetailPage.jsx # Verbatim OCR stream, AI summarizer, and PDF viewer
        ├── AtomsPage.jsx       # Canonical Legal Atoms directory
        ├── AtomDetailPage.jsx  # Proceedings timeline, accused list, and Grounded IRAC Legal Reasoner
        ├── AIResearchPage.jsx  # Dedicated AI Legal Assistant / RAG workspace with court citations
        ├── CourtsPage.jsx      # High Court & Supreme Court jurisdiction coverage
        ├── LongtailPage.jsx    # District courts hierarchical scraper & catalog
        ├── AdminDashboardPage.jsx # Platform control room & pipeline triggers
        ├── ReviewQueuePage.jsx # Human-in-the-loop verification queue
        └── AboutPage.jsx       # Architectural breakdown of CALIP
```

---

## 🚀 How to Run and Develop

### Option A: Unified Mode (FastAPI serves React on `http://localhost:8000`)
1. From the `frontend` folder, build the production bundle:
   ```bash
   cd frontend
   npm run build
   ```
2. Run your FastAPI backend:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Open `http://localhost:8000`. FastAPI will serve the React frontend directly with all API endpoints active.

---

### Option B: Hot-Reload Development Mode (Recommended when editing UI)
1. In one terminal, start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
2. In a second terminal, start the Vite development server:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open `http://localhost:3000`. Changes to React components will update instantly with Hot Module Replacement (HMR), and API calls will be automatically forwarded to port 8000.

---

## 🛠️ Making Changes and Debugging

- **Adding a new API endpoint:** Add a helper method in [src/services/api.js](file:///c:/Users/impra/Desktop/CALIP/frontend/src/services/api.js).
- **Enabling API Console Logs:** Toggle `DEBUG_API = true` inside `api.js` to see all requests and payloads in the browser console.
- **Styling & Theme:** All CSS tokens (colors, border radii, card backgrounds) are defined in [src/index.css](file:///c:/Users/impra/Desktop/CALIP/frontend/src/index.css).
