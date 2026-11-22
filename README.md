# 🚀 DFA Minimization Studio & Simulator

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Vercel](https://img.shields.io/badge/Deployed_on-Vercel-black.svg?logo=vercel&logoColor=white)](https://vercel.com)
[![Render](https://img.shields.io/badge/Hosted_on-Render-46E3B7.svg?logo=render&logoColor=black)](https://render.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An interactive, educational platform and simulation suite for **Theory of Computation** and **Formal Languages**. This tool lets students, educators, and engineers design Deterministic Finite Automata (DFAs), visualize step-by-step state minimization with **Hopcroft's**, **Moore's**, and **Myhill-Nerode Table-Filling** algorithms, and simulate real-time string acceptance across dual state machines.

---

## 📸 Interactive Web Application Showcase

![DFA Minimizer Application Preview](assets/screenshots/demo.png)

*Interactive DFA graph with draggable nodes, active pair highlighting, step-by-step Myhill-Nerode distinguishability matrix, and synchronized playback scrubber.*

---

## ✨ Key Features

- **🎨 Multi-Mode State Designer**:
  - Add, edit, or remove states, alphabet symbols, and transitions interactively.
  - Live transition matrix generation and instant state diagram visualization.
  - Built-in textbook presets (Equivalent states, Unreachable states, Complex multi-cycle DFAs).

- **🧠 Three Minimization Algorithms**:
  - **Hopcroft's Algorithm**: Optimal $O(|\Sigma| \cdot |Q| \log |Q|)$ partition refinement using splitter worklists.
  - **Moore's Algorithm**: Intuitive $O(|\Sigma| \cdot |Q|^2)$ $k$-equivalence signature refinement.
  - **Myhill-Nerode Table-Filling**: Classic lower-triangular matrix marking of distinguishable pairs $(p, q)$.

- **🎬 Interactive Playback Engine**:
  - Step forward, step backward, or auto-play through each minimization iteration.
  - Visual highlight of active splitter blocks, distinguishable pairs, and state mergers.
  - Synchronized mathematical notation and LaTeX step explanations.

- **🧪 Dual-Machine String Verification & Tape Runner**:
  - Run any input string simultaneously through the **Original DFA** and **Minimized DFA**.
  - Traces the state traversal path (`q0 → q1 → q2`) and verifies that language equivalence is strictly preserved.
  - Batch test runner to validate test string suites in one click.

---

## 🏛 Architecture & Project Structure

The project offers two complementary interfaces:
1. **Full-Stack Edition (`/frontend` + `/backend`)**: High-performance React 18 + Vite + Tailwind CSS frontend backed by a FastAPI REST API.
2. **Streamlit Studio (`/dfa_minimization_studio`)**: Lightweight, self-contained Python web app for quick single-click deployment.

```
dfa-minimizer/
├── frontend/                     # Modern React + Vite + Tailwind Web Application
│   ├── src/
│   │   ├── components/           # GraphCard, TableFillingCard, PlaybackBar, Tabs
│   │   ├── services/api.ts       # Backend REST client (with Vercel/Render integration)
│   │   └── presets/              # Sample automata definitions
│   ├── vercel.json               # Vercel SPA routing configuration
│   └── package.json
│
├── backend/                      # High-Performance FastAPI Service
│   ├── app/
│   │   ├── main.py               # REST API endpoints & static asset serving
│   │   ├── models.py             # Pydantic validation schemas
│   │   └── algorithms/           # Trace generators for Step-by-Step UI
│   │       ├── hopcroft.py       # Hopcroft algorithm implementation
│   │       ├── moore.py          # Moore algorithm implementation
│   │       ├── table_filling.py  # Myhill-Nerode table filling algorithm
│   │       ├── simulator.py      # Dual-machine string execution
│   │       └── unreachable.py    # BFS unreachable state pruning
│   ├── requirements.txt          # Backend-specific dependencies
│   └── tests/                    # Automated pytest suite
│
├── dfa_minimization_studio/      # Standalone Streamlit Application
│   ├── app.py                    # Streamlit entrypoint
│   ├── core/                     # Automata engine (DFA, validator, simulator, samples)
│   ├── algorithms/               # Hopcroft & Moore minimizers
│   ├── visualization/            # Graphviz DOT state diagram generators
│   └── ui/                       # Tab views (Designer, Minimizer, Testing, Benchmarks)
│
├── assets/screenshots/           # Screenshots and GIF demos for GitHub
├── requirements.txt              # Unified Python dependencies
├── packages.txt                # Linux container packages (graphviz)
└── run_all.py                    # Simultaneous launcher for local full-stack dev
```

---

## ⚡ Quick Start (Local Setup)

### Option A: Launch Full-Stack Web App (React + FastAPI)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nishtha-1111/dfa-minimizer.git
   cd dfa-minimizer
   ```

2. **Install backend dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Run both backend and frontend concurrently**:
   ```bash
   python run_all.py
   ```
   - **Frontend**: [http://localhost:5173](http://localhost:5173)
   - **Backend API & Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Option B: Launch Streamlit Studio

```bash
pip install -r requirements.txt
streamlit run dfa_minimization_studio/app.py
```
Open **http://localhost:8501** in your browser.

---

## ☁️ Deployment

### 1. Frontend on Vercel + Backend on Render (Recommended)
- **Backend (Render)**:
  - Create a new **Web Service** on [render.com](https://render.com) connected to this repository.
  - Build Command: `pip install -r backend/requirements.txt`
  - Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
  - Copy the deployed URL (e.g. `https://dfa-minimizer-backend.onrender.com`).
- **Frontend (Vercel)**:
  - Import the repository on [vercel.com](https://vercel.com).
  - Set **Root Directory** to `frontend`.
  - Add Environment Variable:
    - `VITE_API_BASE_URL` = `https://<your-render-backend-url>`
  - Click **Deploy**.

### 2. Standalone Streamlit Cloud
- Connect repository on [share.streamlit.io](https://share.streamlit.io) and set the main file to `dfa_minimization_studio/app.py`.

---

## 🧪 Testing

Run the automated test suites to verify reachability pruning, state equivalence, and string simulation:

```bash
# Backend API tests
python -m pytest backend/tests -v

# Minimization Studio algorithms tests
python -m pytest dfa_minimization_studio/tests -v
```

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
