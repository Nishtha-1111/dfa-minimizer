import React, { useState, useEffect, useRef, useMemo } from 'react';
import { DFADefinition } from '../../types/dfa';
import { PRESET_DFAS } from '../../presets/sampleDfas';
import { RotateCcw, ZoomIn, ZoomOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface GraphCardProps {
  originalDfa: DFADefinition;
  minimizedDfa?: DFADefinition;
  viewMode: 'original' | 'minimized';
  onViewModeChange: (mode: 'original' | 'minimized') => void;
  activeSplitterBlock?: string[];
  highlightedStates?: string[];
  unreachableStates?: string[];
  activePair?: string[];
  targetPair?: string[];
  isFinalStep?: boolean;
}

interface NodePos {
  x: number;
  y: number;
}

export const GraphCard: React.FC<GraphCardProps> = ({
  originalDfa,
  minimizedDfa,
  viewMode,
  onViewModeChange,
  activeSplitterBlock = [],
  highlightedStates = [],
  unreachableStates = [],
  activePair = [],
  targetPair = [],
  isFinalStep = false,
}) => {
  const currentDfa = viewMode === 'minimized' && minimizedDfa ? minimizedDfa : originalDfa;
  const svgRef = useRef<SVGSVGElement>(null);

  // Auto-switch to Minimized on final step if available
  useEffect(() => {
    if (isFinalStep && minimizedDfa && viewMode !== 'minimized') {
      onViewModeChange('minimized');
    }
  }, [isFinalStep, minimizedDfa, viewMode, onViewModeChange]);

  // Positions state to support dragging
  const [positions, setPositions] = useState<Record<string, NodePos>>({});
  const [draggingNode, setDraggingNode] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Interactive selection & zoom
  const [selectedState, setSelectedState] = useState<string | null>(null);
  const [hoveredState, setHoveredState] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  // Compute layout
  const resetLayout = () => {
    const states = currentDfa.states;
    const count = states.length;
    const initialPos: Record<string, NodePos> = {};

    if (viewMode === 'original' && PRESET_DFAS.textbook.layout) {
      const tbLayout = PRESET_DFAS.textbook.layout;
      let matches = true;
      for (const s of states) {
        if (!tbLayout[s]) {
          matches = false;
          break;
        }
      }
      if (matches) {
        setPositions({ ...tbLayout });
        return;
      }
    }

    if (viewMode === 'minimized') {
      if (count === 3) {
        setPositions({
          [states[0]]: { x: 160, y: 260 },
          [states[1]]: { x: 330, y: 170 },
          [states[2]]: { x: 490, y: 260 },
        });
        return;
      }
      if (count === 1) {
        setPositions({ [states[0]]: { x: 320, y: 260 } });
        return;
      }
      if (count === 2) {
        setPositions({
          [states[0]]: { x: 220, y: 260 },
          [states[1]]: { x: 420, y: 260 },
        });
        return;
      }
    }

    const width = 640;
    const height = 480;
    const cx = width / 2;
    const cy = height / 2;
    const r = Math.min(width, height) * 0.35;

    states.forEach((state, i) => {
      const angle = (2 * Math.PI * i) / count - Math.PI / 2;
      initialPos[state] = {
        x: Math.round(cx + r * Math.cos(angle)),
        y: Math.round(cy + r * Math.sin(angle)),
      };
    });

    setPositions(initialPos);
  };

  useEffect(() => {
    resetLayout();
    setSelectedState(null);
  }, [currentDfa, viewMode]);

  // Drag Handlers
  const handleMouseDown = (state: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const mouseX = ((e.clientX - rect.left) / rect.width) * 640;
    const mouseY = ((e.clientY - rect.top) / rect.height) * 500;
    const pos = positions[state] || { x: 0, y: 0 };
    setDraggingNode(state);
    setDragOffset({ x: mouseX - pos.x, y: mouseY - pos.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!draggingNode || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const mouseX = ((e.clientX - rect.left) / rect.width) * 640;
    const mouseY = ((e.clientY - rect.top) / rect.height) * 500;

    const newX = Math.max(45, Math.min(595, mouseX - dragOffset.x));
    const newY = Math.max(45, Math.min(455, mouseY - dragOffset.y));

    setPositions((prev) => ({
      ...prev,
      [draggingNode]: { x: Math.round(newX), y: Math.round(newY) },
    }));
  };

  const handleMouseUp = () => {
    setDraggingNode(null);
  };

  // Group transitions into labels like "0,1"
  const edges = useMemo(() => {
    const pairMap = new Map<string, { from: string; to: string; symbols: string[] }>();

    for (const fromState of currentDfa.states) {
      const trans = currentDfa.transitions[fromState] || {};
      for (const sym of currentDfa.alphabet) {
        const toState = trans[sym];
        if (!toState || !positions[toState]) continue;

        const key = `${fromState}->${toState}`;
        if (!pairMap.has(key)) {
          pairMap.set(key, { from: fromState, to: toState, symbols: [] });
        }
        if (!pairMap.get(key)!.symbols.includes(sym)) {
          pairMap.get(key)!.symbols.push(sym);
        }
      }
    }

    return Array.from(pairMap.values()).map((e) => ({
      ...e,
      label: e.symbols.sort().join(','),
    }));
  }, [currentDfa, positions]);

  const splitterLegendText = useMemo(() => {
    if (!activeSplitterBlock || activeSplitterBlock.length === 0) return null;
    return `Splitter block: ${[...activeSplitterBlock].sort().join(', ')}`;
  }, [activeSplitterBlock]);

  const NODE_RADIUS = 26;

  // Active pair coords for linking dashed beam
  const activePairCoords = useMemo(() => {
    if (!activePair || activePair.length < 2) return null;
    const p1 = positions[activePair[0]];
    const p2 = positions[activePair[1]];
    if (!p1 || !p2) return null;
    return { p1, p2 };
  }, [activePair, positions]);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-full overflow-hidden">
      {/* Header with Title, Mode Segment, and Canvas Controls */}
      <div className="flex items-center justify-between px-7 py-4 border-b border-slate-100 select-none">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-bold text-slate-800 tracking-tight">DFA graph</h2>
          <span className="text-xs text-slate-400 font-medium hidden md:inline">
            (drag nodes to arrange • click node to inspect)
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Zoom & Reset Toolbar */}
          <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-xl p-1 text-slate-500">
            <button
              onClick={() => setZoomLevel((z) => Math.max(0.75, z - 0.1))}
              className="p-1 hover:text-slate-800 rounded transition-colors"
              title="Zoom out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoomLevel((z) => Math.min(1.4, z + 0.1))}
              className="p-1 hover:text-slate-800 rounded transition-colors"
              title="Zoom in"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => {
                resetLayout();
                setZoomLevel(1);
              }}
              className="p-1 hover:text-slate-800 rounded transition-colors border-l border-slate-200 ml-1"
              title="Reset layout to default"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Toggle [ Original | Minimized ] */}
          <div className="flex bg-slate-100 p-1 rounded-xl text-xs font-semibold text-slate-600">
            <button
              onClick={() => onViewModeChange('original')}
              className={`px-3.5 py-1.5 rounded-lg transition-all ${
                viewMode === 'original'
                  ? 'bg-white text-blue-600 shadow-sm font-bold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Original
            </button>
            <button
              onClick={() => onViewModeChange('minimized')}
              disabled={!minimizedDfa}
              className={`px-3.5 py-1.5 rounded-lg transition-all ${
                !minimizedDfa
                  ? 'opacity-40 cursor-not-allowed text-slate-400'
                  : viewMode === 'minimized'
                  ? 'bg-white text-blue-600 shadow-sm font-bold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Minimized
            </button>
          </div>
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div
        className="flex-1 relative flex items-center justify-center p-4 min-h-[440px] bg-white cursor-default select-none overflow-hidden"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onClick={() => setSelectedState(null)}
      >
        <svg
          ref={svgRef}
          viewBox="0 0 640 500"
          className="w-full h-full max-h-[480px] select-none transition-transform duration-150"
          style={{
            overflow: 'visible',
            transform: `scale(${zoomLevel})`,
            transformOrigin: 'center center',
          }}
        >
          <defs>
            <marker
              id="arrowhead-slate"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#64748B" />
            </marker>
            <marker
              id="arrowhead-start"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#3B82F6" />
            </marker>
            <marker
              id="arrowhead-highlight"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#2563EB" />
            </marker>
            <marker
              id="arrowhead-amber"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#D97706" />
            </marker>

            {/* Animated Flow Filter / Glow */}
            <filter id="glow-pulse" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Active Pair Comparison Beam (during Table-Filling) */}
          {activePairCoords && (
            <g>
              <line
                x1={activePairCoords.p1.x}
                y1={activePairCoords.p1.y}
                x2={activePairCoords.p2.x}
                y2={activePairCoords.p2.y}
                stroke="#F59E0B"
                strokeWidth="2.5"
                strokeDasharray="6 4"
                className="opacity-70 animate-pulse"
              />
            </g>
          )}

          {/* Start State Indicator Arrow */}
          {positions[currentDfa.start_state] && (
            <g>
              <line
                x1={positions[currentDfa.start_state].x - 65}
                y1={positions[currentDfa.start_state].y}
                x2={positions[currentDfa.start_state].x - NODE_RADIUS - 4}
                y2={positions[currentDfa.start_state].y}
                stroke="#3B82F6"
                strokeWidth="2.5"
                markerEnd="url(#arrowhead-start)"
              />
            </g>
          )}

          {/* Transitions (Edges) */}
          {edges.map((edge, idx) => {
            const fromPos = positions[edge.from];
            const toPos = positions[edge.to];
            if (!fromPos || !toPos) return null;

            const isSelfLoop = edge.from === edge.to;
            const isUserInspected =
              selectedState === edge.from ||
              selectedState === edge.to ||
              hoveredState === edge.from;

            const isAlgoActiveEdge =
              (activePair.includes(edge.from) && targetPair.includes(edge.to)) ||
              (activePair.includes(edge.from) && activePair.includes(edge.to));

            let strokeColor = '#64748B';
            let strokeWidth = 2;
            let marker = 'url(#arrowhead-slate)';
            let isAnimatedDash = false;

            if (isAlgoActiveEdge) {
              strokeColor = '#D97706';
              strokeWidth = 3;
              marker = 'url(#arrowhead-amber)';
              isAnimatedDash = true;
            } else if (isUserInspected) {
              strokeColor = '#2563EB';
              strokeWidth = 2.8;
              marker = 'url(#arrowhead-highlight)';
            }

            if (isSelfLoop) {
              const loopX = fromPos.x;
              const loopY = fromPos.y - NODE_RADIUS - 6;
              return (
                <g key={`edge-${idx}`}>
                  <path
                    d={`M ${fromPos.x - 12} ${fromPos.y - NODE_RADIUS} C ${fromPos.x - 28} ${
                      fromPos.y - NODE_RADIUS - 36
                    }, ${fromPos.x + 28} ${fromPos.y - NODE_RADIUS - 36}, ${fromPos.x + 12} ${
                      fromPos.y - NODE_RADIUS
                    }`}
                    fill="none"
                    stroke={strokeColor}
                    strokeWidth={strokeWidth}
                    markerEnd={marker}
                    strokeDasharray={isAnimatedDash ? '6 4' : undefined}
                    className={isAnimatedDash ? 'animate-pulse' : undefined}
                  />
                  <rect
                    x={loopX - 14}
                    y={loopY - 22}
                    width={28}
                    height={18}
                    rx={5}
                    fill="#FFFFFF"
                    stroke={isUserInspected || isAlgoActiveEdge ? '#93C5FD' : '#E2E8F0'}
                    strokeWidth="1"
                  />
                  <text
                    x={loopX}
                    y={loopY - 9}
                    textAnchor="middle"
                    fill={isUserInspected ? '#1E40AF' : '#334155'}
                    fontSize="13"
                    fontWeight="700"
                  >
                    {edge.label}
                  </text>
                </g>
              );
            }

            const dx = toPos.x - fromPos.x;
            const dy = toPos.y - fromPos.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist === 0) return null;

            const ux = dx / dist;
            const uy = dy / dist;
            const nx = -uy;
            const ny = ux;

            const hasOpposite = edges.some((e) => e.from === edge.to && e.to === edge.from);
            const curveOffset = hasOpposite ? 26 : 0;

            const mx = (fromPos.x + toPos.x) / 2 + nx * curveOffset;
            const my = (fromPos.y + toPos.y) / 2 + ny * curveOffset;

            const startX = fromPos.x + ux * NODE_RADIUS;
            const startY = fromPos.y + uy * NODE_RADIUS;
            const endX = toPos.x - ux * (NODE_RADIUS + 4);
            const endY = toPos.y - uy * (NODE_RADIUS + 4);

            const pathD =
              curveOffset !== 0
                ? `M ${startX} ${startY} Q ${mx} ${my} ${endX} ${endY}`
                : `M ${startX} ${startY} L ${endX} ${endY}`;

            return (
              <g key={`edge-${idx}`}>
                <path
                  d={pathD}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  markerEnd={marker}
                  strokeDasharray={isAnimatedDash ? '6 4' : undefined}
                  className={isAnimatedDash ? 'animate-pulse' : undefined}
                />
                <rect
                  x={mx - (edge.label.length > 2 ? 18 : 13)}
                  y={my - 11}
                  width={edge.label.length > 2 ? 36 : 26}
                  height={20}
                  rx={5}
                  fill="#FFFFFF"
                  stroke={isUserInspected || isAlgoActiveEdge ? '#93C5FD' : '#E2E8F0'}
                  strokeWidth="1"
                />
                <text
                  x={mx}
                  y={my + 4}
                  textAnchor="middle"
                  fill={isUserInspected ? '#1E40AF' : '#1E293B'}
                  fontSize="13"
                  fontWeight="700"
                >
                  {edge.label}
                </text>
              </g>
            );
          })}

          {/* State Nodes (Draggable + Realistic Glow) */}
          {currentDfa.states.map((state) => {
            const pos = positions[state];
            if (!pos) return null;

            const isAccepting = currentDfa.accept_states.includes(state);
            const isInSplitter =
              viewMode === 'original' && activeSplitterBlock.includes(state);
            const isInActivePair = activePair.includes(state);
            const isUnreachable = unreachableStates.includes(state);
            const isSelected = selectedState === state;

            let fillColor = '#EFF6FF'; // light blue
            let strokeColor = '#3B82F6'; // blue
            let textColor = '#1E40AF';

            if (isInActivePair || isInSplitter) {
              fillColor = '#FEF3C7'; // warm amber/yellow
              strokeColor = '#D97706'; // dark amber
              textColor = '#92400E';
            } else if (isAccepting && viewMode === 'minimized') {
              fillColor = '#FEF3C7';
              strokeColor = '#D97706';
              textColor = '#92400E';
            }

            if (isSelected) {
              strokeColor = '#1D4ED8';
            }

            return (
              <g
                key={`node-${state}`}
                className={`transition-opacity duration-300 ${
                  isUnreachable ? 'opacity-25' : 'opacity-100'
                } cursor-grab active:cursor-grabbing hover:scale-105`}
                transform={`translate(${pos.x}, ${pos.y})`}
                onMouseDown={(e) => handleMouseDown(state, e)}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedState(isSelected ? null : state);
                }}
                onMouseEnter={() => setHoveredState(state)}
                onMouseLeave={() => setHoveredState(null)}
              >
                {/* Active Pair / Splitter Pulse Ring */}
                {(isInActivePair || isInSplitter) && (
                  <circle
                    r={NODE_RADIUS + 7}
                    fill="none"
                    stroke="#F59E0B"
                    strokeWidth="2"
                    strokeDasharray="4 3"
                    className="animate-spin"
                    style={{ animationDuration: '6s' }}
                  />
                )}

                {/* Outer circle */}
                <circle
                  r={NODE_RADIUS}
                  fill={fillColor}
                  stroke={strokeColor}
                  strokeWidth={isInSplitter || isInActivePair || isSelected ? 3.5 : 2.5}
                />

                {/* Double ring for accepting state */}
                {isAccepting && (
                  <circle
                    r={NODE_RADIUS - 5}
                    fill="none"
                    stroke={strokeColor}
                    strokeWidth={isInSplitter || isInActivePair || isSelected ? 2.5 : 2}
                  />
                )}

                {/* State Label */}
                <text
                  textAnchor="middle"
                  dy=".34em"
                  fontSize={state.length > 4 ? '11' : '16'}
                  fontWeight="700"
                  fill={textColor}
                  className="font-sans select-none pointer-events-none"
                >
                  {state}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Selected State Inspection Pill */}
        {selectedState && (
          <div className="absolute top-4 left-6 bg-white/95 backdrop-blur-sm border border-blue-200 shadow-md rounded-xl px-4 py-2 text-xs font-medium text-slate-700 flex items-center gap-3">
            <span>
              Inspecting state <strong className="font-mono text-blue-700 text-sm font-bold">{selectedState}</strong>:
            </span>
            <div className="flex items-center gap-2 font-mono">
              {currentDfa.alphabet.map((sym) => (
                <span key={sym} className="px-2 py-0.5 bg-blue-50 border border-blue-200 rounded text-blue-800">
                  {sym} → {currentDfa.transitions[selectedState]?.[sym] || 'None'}
                </span>
              ))}
            </div>
            <button
              onClick={() => setSelectedState(null)}
              className="text-slate-400 hover:text-slate-700 font-bold ml-1"
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {/* Bottom Legend */}
      <div className="flex flex-wrap items-center justify-between px-7 py-3.5 border-t border-slate-100 text-sm font-medium text-slate-600 bg-slate-50/60 select-none">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="inline-block w-4 h-4 rounded-full border-2 border-slate-400 bg-white" />
            <span>State</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="relative inline-flex items-center justify-center w-4 h-4 rounded-full border-2 border-slate-400 bg-white">
              <span className="w-1.5 h-1.5 rounded-full border border-slate-400" />
            </span>
            <span>Accepting</span>
          </div>
          {splitterLegendText && (
            <div className="flex items-center gap-2 text-amber-700">
              <span className="inline-block w-3.5 h-3.5 rounded-full bg-amber-600" />
              <span className="font-bold">{splitterLegendText}</span>
            </div>
          )}
        </div>

        <div className="text-xs text-slate-400">
          Showing {currentDfa.states.length} states • {edges.length} transition edges
        </div>
      </div>
    </div>
  );
};
