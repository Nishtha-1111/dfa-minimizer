# DFA Minimization Studio — Full Documentation

Welcome to the comprehensive technical documentation for the **DFA Minimization Studio**. This documentation details the mathematical theory, algorithms, backend architecture, frontend implementation, and interactive visual components.

---

## Documentation Index

| File | Content Summary |
|---|---|
| [**1. Algorithms & Automata Theory**](./algorithms.md) | In-depth theory of Myhill-Nerode Table-Filling, Moore's Partition Refinement, BFS Unreachable State Elimination, and Dual-DFA String Simulation. |
| [**2. Backend Architecture**](./backend.md) | FastAPI REST service, Pydantic schemas, validation engine, trace generator, and pytest test suite. |
| [**3. Frontend Architecture**](./frontend.md) | React 18 + Vite + Tailwind CSS + Framer Motion components, SVG graph renderer, animated triangular table, tape runner, and design system. |

---

## System Overview & Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        REACT FRONTEND (Vite)                           │
│                                                                        │
│  [TopBar]            Logo + "DFA Minimizer"                            │
│  [ControlBar]        [ Table-Filling | Moore ] | Reset | Minimize      │
│  [TabNavigation]     1. Input  |  2. Visualize  |  3. Test Strings     │
│                                                                        │
│  ┌───────────────────────┐  ┌───────────────────────────────────────┐  │
│  │     GRAPH CARD        │  │     TABLE OR GROUPS CARD              │  │
│  │  - Draggable SVG nodes│  │  - Lower-Triangular Table (Myhill)    │  │
│  │  - Active pair beam   │  │  - Partition Blocks (Moore)           │  │
│  │  - Edge flow particles│  │  - Step Explanation & LaTeX Notation  │  │
│  └───────────────────────┘  └───────────────────────────────────────┘  │
│                                                                        │
│  [Sticky Playback Bar]  Back | Play/Pause | Next | Scrubber | Speed    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ JSON / REST HTTP
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND (Python)                        │
│                                                                        │
│  • POST /api/validate   -> Checks symbol consistency & transitions     │
│  • POST /api/minimize   -> Unreachable removal + Algorithm Trace       │
│  • POST /api/simulate   -> Dual-machine string execution & tape steps  │
│  • GET  /api/health     -> Service status check                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start & Running

Launch both the **FastAPI backend** (`http://127.0.0.1:8000`) and the **React frontend** (`http://localhost:5173`) simultaneously:

```powershell
python run_all.py
```

### Running Backend Independently
```powershell
uvicorn backend.app.main:app --reload --port 8000
```
- Interactive Swagger API Explorer: `http://127.0.0.1:8000/docs`

### Running Frontend Independently
```powershell
cd frontend
npm run dev
```

### Running Automated Test Suite
```powershell
$env:PYTHONPATH="."
python -m pytest backend/tests/test_api.py -v
```
