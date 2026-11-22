# 🚀 DFA Minimization Studio & Simulator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An interactive, educational platform and simulation suite for **Theory of Computation** and **Formal Languages**. This tool lets students, educators, and engineers design Deterministic Finite Automata (DFAs), visualize step-by-step state minimization with **Hopcroft's**, **Moore's**, and **Myhill-Nerode Table-Filling** algorithms, and simulate real-time string acceptance across dual state machines.

---

## 📸 Demo & Screenshots

> **Live Demo**: [Deploy or View on Streamlit Cloud](https://share.streamlit.io)

| 1. Interactive Minimization & Graph Visualization |
|:---:|
| ![Minimization Studio Preview](assets/screenshots/demo.png) |
| *Step-by-step state partition refinement with animated graph rendering and mathematical explanations.* |

| 2. Dual DFA String Simulator | 3. Lower Triangular Myhill-Nerode Table |
|:---:|:---:|
| ![Tape Runner & Test Strings](assets/screenshots/simulator.png) | ![Table Filling Method](assets/screenshots/table_filling.png) |
| *Real-time parallel string execution on Original vs. Minimized DFA.* | *Distinguishable state pair marking matrix.* |

*(Place your recorded screenshots or GIFs inside `assets/screenshots/` to display them here)*

---

## ✨ Key Features

- **🎨 Multi-Mode State Designer**:
  - Add, edit, or remove states, alphabet symbols, and transitions.
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
  - Batch test runner to validate language suites in one click.

---

## 🏛 Architecture & Project Structure

The project offers two complementary interfaces:
1. **Streamlit Studio (`/dfa_minimization_studio`)**: Lightweight, self-contained Python web app ideal for single-click free hosting on Streamlit Cloud.
2. **Full-Stack Edition (`/frontend` + `/backend`)**: High-performance React 18 + Vite + Tailwind CSS frontend backed by a FastAPI REST API.

```
Simulator_AOT/
├── dfa_minimization_studio/      # Standalone Streamlit Application
│   ├── app.py                    # Streamlit entrypoint
│   ├── core/                     # Automata engine (DFA, validator, simulator, presets)
│   ├── algorithms/               # Hopcroft, Moore, and Minimizer implementations
│   ├── visualization/            # Graphviz DOT state diagram generators
│   └── ui/                       # Tab views (Designer, Minimizer, Testing, Benchmarks)
│
├── backend/                      # High-Performance FastAPI Service
│   ├── app/
│   │   ├── main.py               # REST API endpoints (/api/validate, /api/minimize, /api/simulate)
│   │   ├── models.py             # Pydantic validation schemas
│   │   └── algorithms/           # Trace generators for Step-by-Step UI
│   └── tests/                    # Automated pytest suite
│
├── frontend/                     # Modern React + Vite + Tailwind Web Application
│   ├── src/
│   │   ├── components/           # GraphCard, TableFillingCard, PlaybackBar, Tabs
│   │   ├── services/api.ts       # Backend REST client
│   │   └── presets/              # Sample automata definitions
│   └── package.json
│
├── assets/screenshots/           # Screenshots and GIF demos for GitHub
├── requirements.txt              # Python dependencies
├── packages.txt                # Linux container system packages (graphviz)
└── run_all.py                    # Simultaneous launcher for local full-stack dev
```

---

## ⚡ Quick Start (Local Setup)

### Option A: Launch Streamlit Studio (Easiest)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/Simulator_AOT.git
   cd Simulator_AOT
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Streamlit**:
   ```bash
   streamlit run dfa_minimization_studio/app.py
   ```
   Open **http://localhost:8501** in your browser.

---

### Option B: Launch Full-Stack Web App (React + FastAPI)

1. **Install backend dependencies**:
   ```bash
   pip install fastapi "uvicorn[standard]" pydantic pytest
   ```

2. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Run both backend and frontend concurrently**:
   ```bash
   python run_all.py
   ```
   - **Frontend**: [http://localhost:5173](http://localhost:5173)
   - **Backend API & Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## ☁️ Deployment

### 1. Free Deployment on Streamlit Community Cloud
1. Push your repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Select this repository and set **Main file path** to:
   ```text
   dfa_minimization_studio/app.py
   ```
4. Click **Deploy!**

### 2. Full-Stack Deployment (Vercel + Render)
- **Backend (FastAPI)**: Deploy to [Render.com](https://render.com) as a Web Service (`uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`).
- **Frontend (React)**: Deploy to [Vercel](https://vercel.com) with root directory set to `frontend/`.

---

## 🧪 Testing

Run automated tests to verify algorithm correctness, reachability pruning, and language equivalence:

```bash
# Run backend API tests
python -m pytest backend/tests -v

# Run studio algorithms tests
python -m pytest dfa_minimization_studio/tests -v
```

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
