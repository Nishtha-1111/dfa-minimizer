# Frontend Architecture & Interactive Components

This document details the frontend implementation of the **DFA Minimizer**, covering UI components, SVG graph rendering, animations, state management, and the design system.

---

## 1. Technology Stack

- **Framework**: React 18 (TypeScript)
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS
- **Animation**: Framer Motion
- **Math Rendering**: KaTeX (`katex/dist/katex.min.css`)
- **Icons**: Lucide React

---

## 2. Component Hierarchy

```
App.tsx
├── TopBar
├── ControlBar
├── TabNavigation
└── Main Tab Container
    ├── [Tab 1] InputTab
    │   ├── PresetChips (Textbook, Already Minimal, Unreachable, Divisible by 3)
    │   ├── AlphabetEditor (Comma-separated symbols)
    │   ├── TransitionTableEditor (Add/Remove state, start radio, accept toggle, dropdowns)
    │   └── LiveValidationBanner (Autofill Dead State button)
    │
    ├── [Tab 2] Visualize (Two-Column Layout)
    │   ├── Left Column: GraphCard
    │   │   ├── Original | Minimized Toggle
    │   │   ├── Zoom & Reset Controls (+ / - / ⟲)
    │   │   ├── SVG Graph Canvas
    │   │   │   ├── Draggable State Nodes (Single / Double circles for accepting)
    │   │   │   ├── Curved Transitions & Self-loops (Merged labels e.g. "0, 1")
    │   │   │   ├── Active Comparison Laser Beam (Connecting evaluated pair {p, q})
    │   │   │   ├── Animated Transition Flow Particles (Moving dashes on active edge)
    │   │   │   └── Rotating Glowing Pulse Rings (On active states / splitters)
    │   │   └── Legend (Normal state, Accepting, Active pair, etc.)
    │   │
    │   └── Right Column:
    │       ├── View Switcher (Distinguishability Table vs Groups of States)
    │       ├── TableFillingCard (Lower-triangular matrix with spring ✕ stamps)
    │       │   OR GroupsCard (Partition blocks with amber splitter highlight)
    │       └── ExplanationCard (Plain-English text, progress bar, KaTeX notation)
    │
    └── [Tab 3] TestStringsTab
        ├── Single String Tester with Character Tape Stepper
        ├── Dual Path State Indicator (Original vs Minimized)
        ├── Acceptance Agreement Banner
        └── Batch Test Suite (Multi-line test strings)
    
└── Sticky PlaybackBar
    ├── Step Counter ("Step N of M")
    ├── Controls (Back, Play/Pause, Next)
    ├── Interactive Scrubber Track
    ├── Speed Selector (0.5x, 1x, 2x)
    └── Keyboard Shortcuts (Space = Play/Pause, Left/Right = Step)
```

---

## 3. Key Interactive Components

### 1. `GraphCard.tsx` (SVG Canvas & Force Layout)
- **Node Dragging**: Users can drag nodes to adjust the graph layout. Positions are tracked in local state.
- **Comparison Laser Beam**: When Table-Filling tests a pair $\{p, q\}$, a glowing dashed amber beam connects both nodes in real time.
- **Particle Flow on Transitions**: Active transitions feature animated moving dashes using SVG stroke dasharray animations:
  ```css
  stroke-dasharray: 6 4;
  animation: dash 1s linear infinite;
  ```
- **Accepting States**: Rendered with canonical double circles (outer radius $R$, inner radius $R - 5$).
- **Click-to-Inspect**: Clicking any node opens a popup showing all outgoing transitions.

---

### 2. `TableFillingCard.tsx` (Lower-Triangular Distinguishability Matrix)
- **Canonical Structure**:
  - Displays states $q_1 \dots q_{n-1}$ on rows and $q_0 \dots q_{n-2}$ on columns.
- **Framer Motion Stamps**:
  - Distinguishable cells animate in with a spring-loaded **`✕`** stamp:
  ```tsx
  <motion.span
    initial={{ scale: 0, rotate: -45 }}
    animate={{ scale: 1, rotate: 0 }}
    transition={{ type: 'spring', stiffness: 450, damping: 20 }}
  >
    ✕
  </motion.span>
  ```
- **Active & Target Pair Highlighting**:
  - The cell currently being evaluated $\{p, q\}$ pulses with a gold border.
  - The witness cell $\{p', q'\}$ that caused the mark is highlighted in blue with an explanatory caption.

---

### 3. `TestStringsTab.tsx` (Interactive Character Tape Stepper)
- **Visual Tape Head**: Displays the input string as a tape of discrete character cells.
- **Simultaneous Step Execution**: Stepping through the tape updates the tape head position while highlighting the active state on both the original DFA and the minimal DFA.
- **Agreement Verification**: Displays a green badge confirming that both machines agree on acceptance.

---

## 4. Design System & Typography

- **Strict Light Theme**:
  - Background: `#F8FAFC` (Slate 50)
  - Card Surfaces: `#FFFFFF` (Pure white)
  - Borders: `1px solid #E2E8F0` (Slate 200)
  - Primary Accent: `#2563EB` (Blue 600)
  - Highlight / Splitter Accent: `#D97706` / `#FEF3C7` (Amber)
  - Text: `#0F172A` (Slate 900) and `#475569` (Slate 600)
- **Humanized Typography Scale**:
  - Base body font: **15–16px**
  - Section headings: **18–20px**
  - Step explanation text: **16px**
  - Table cells and transition dropdowns: **14px**
