# DFA Minimization Studio

An interactive, educational web application for Theory of Computation and Formal Languages, built with **Python**, **Streamlit**, and **Graphviz**, featuring a minimal, elegant **Teal, Cream, and Navy Blue** design.

---

## 🎨 Color Palette & Design

| Role | Color | Hex Code | Usage |
|---|---|---|---|
| Primary | **Teal** | `#2A9D8F` | Primary buttons, active highlights, start arrow |
| Background | **Cream** | `#F5F0E6` | Main application background and cards |
| Typography | **Navy Blue** | `#142B45` | Headings, text, navigation tabs, node outlines |
| Highlight | **Light Teal** | `#D8EDE8` | Selected partitions, badges, active step pills |
| Base | **White** | `#FFFFFF` | Input fields, card backgrounds, node fills |

---

## 📂 Project Architecture

```
dfa_minimization_studio/
├── app.py                      # Main Streamlit application and tab orchestrator
├── requirements.txt            # Dependencies (streamlit)
│
├── core/
│   ├── dfa.py                  # Formal DFA tuple M = (Q, Σ, δ, q0, F)
│   ├── validator.py            # Validation, unreachable state removal, dead-state fix
│   ├── simulator.py            # Single-string & batch tape execution
│   └── samples.py              # 6 textbook & complex benchmark sample DFAs
│
├── algorithms/
│   ├── hopcroft.py             # Genuine O(|Σ| · |Q| log |Q|) partition refinement
│   ├── moore.py                # Genuine O(|Σ| · |Q|²) k-equivalence signatures
│   └── minimizer.py            # Minimization coordinator and comparative benchmarking
│
├── visualization/
│   └── graph_visualizer.py     # Graphviz DOT generator with double circles & curved edges
│
├── ui/
│   ├── home.py                 # Tab 1: Educational introduction & workflow
│   ├── dfa_designer.py         # Tab 2: State/alphabet/transition/table editor + live preview
│   ├── algorithm_selection.py  # Tab 3: Hopcroft vs Moore interactive cards
│   ├── minimization.py         # Tab 4: Final Answer & Step-by-Step Explanation modes
│   ├── testing.py              # Tab 5: Single & batch string simulation
│   └── comparison.py           # Tab 6: Side-by-side metric comparison
│
└── assets/
    └── styles.css              # Custom CSS theme for Streamlit
```

---

## 🚀 How to Run

### Option 1: Quick Launcher (From Repository Root)
```powershell
python run_studio.py
```

### Option 2: Direct Streamlit Run
```powershell
streamlit run dfa_minimization_studio/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 Running Unit Tests
```powershell
python -m pytest dfa_minimization_studio/tests -v
```
All unit tests verify:
- Hopcroft and Moore partition refinement correctness
- Reachability BFS pruning of unreachable states
- Language equivalence on test string suites
- Edge cases (single-state, all-accept, no-accept, incomplete DFAs)
