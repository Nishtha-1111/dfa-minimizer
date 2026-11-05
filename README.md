# DFA Minimizer Studio & Interactive Visualizer

A modern, educational DFA minimization tool built according to the clean, guided Light layout specifications with Hopcroft's and Moore's algorithms.

## Visual Design Overview
The interface matches the uploaded design specifications:
- **Top Bar**: Clean header with `δ DFA Minimizer`, `Export` dropdown (JSON/DOT), and `Light`/`Dark` theme toggle.
- **Control Bar**:
  - `Example` preset dropdown (`Textbook (equivalent states)`, `Already minimal`, `Unreachable states`, `Divisible by 3`, `All merge`, `8-State Complex`).
  - Segmented control: `[ Hopcroft | Moore ]`.
  - `Reset` and solid blue `Minimize` buttons.
- **3 Tab Navigation**:
  - `1. Input`: Interactive transition table editor, start/accept state selectors, validation & "Autofill Dead State".
  - `2. Visualize`:
    - **Left Column ("DFA graph")**: Clean SVG directed graph with `[ Original | Minimized ]` toggle, accepting double rings, amber splitter block highlighting (`{C, D}`), and legend (`○ State`, `◎ Accepting`, `● Splitter block: C, D`).
    - **Right Column ("Groups of states")**: Partition cards with active `Splitter` badge, and **Step Explanation** card with plain-English reasoning and collapsible `▸ Show formal notation`.
  - **Sticky Playback Bar**: `◀ Back`, `▶ Play / ⏸ Pause`, `Next ▶`, interactive progress scrubber, and speed selector (`0.5x`, `1x`, `1.5x`, `2x`).
  - `3. Test strings`: Single string simulation with path traversal on both Original and Minimized DFAs, plus automated equivalence test suite.

---

## Quick Start

### 1. Launch React Frontend (Matching Screenshot)
```bash
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 2. Launch Streamlit Studio
```bash
python run_studio.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 3. Run Automated Tests
```bash
python -m pytest dfa_minimization_studio/tests -v
```
All unit tests verify:
- BFS unreachable state removal
- Completeness validation & dead state addition
- Hopcroft's $O(|\Sigma| \cdot |Q| \log |Q|)$ partition refinement
- Moore's $O(|\Sigma| \cdot |Q|^2)$ $k$-equivalence signature refinement
- Language preservation across all sample DFAs
