import React, { useState, useEffect, useRef, useCallback } from 'react';
import { TopBar } from './components/layout/TopBar';
import { ControlBar } from './components/layout/ControlBar';
import { TabNavigation, ActiveTab } from './components/tabs/TabNavigation';
import { GraphCard } from './components/visualize/GraphCard';
import { GroupsCard } from './components/visualize/GroupsCard';
import { TableFillingCard } from './components/visualize/TableFillingCard';
import { ExplanationCard } from './components/visualize/ExplanationCard';
import { PlaybackBar } from './components/controls/PlaybackBar';
import { InputTab } from './components/tabs/InputTab';
import { TestStringsTab } from './components/tabs/TestStringsTab';

import { DFADefinition, AlgorithmType, MinimizeResponse, ValidationResponse } from './types/dfa';
import { PRESET_DFAS } from './presets/sampleDfas';
import { validateDfa, minimizeDfa } from './services/api';
import { AlertCircle, Sparkles } from 'lucide-react';

export const App: React.FC = () => {
  // 1. Default textbook DFA
  const defaultDfa: DFADefinition = PRESET_DFAS.textbook.dfa;

  // DFA & Algorithm State (Default to Table-Filling)
  const [currentDfa, setCurrentDfa] = useState<DFADefinition>(defaultDfa);
  const [algorithm, setAlgorithm] = useState<AlgorithmType>('table_filling');

  // Validation State
  const [validation, setValidation] = useState<ValidationResponse | null>(null);

  // Minimization Result & Trace State
  const [minimizeResult, setMinimizeResult] = useState<MinimizeResponse | null>(null);
  const [isMinimizing, setIsMinimizing] = useState<boolean>(false);
  const [minimizeError, setMinimizeError] = useState<string | null>(null);

  // Playback & Step State
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [viewMode, setViewMode] = useState<'original' | 'minimized'>('original');

  // Right column view toggle: Table-filling grid vs Groups
  const [rightViewMode, setRightViewMode] = useState<'table' | 'groups'>('table');

  // Navigation Tab
  const [activeTab, setActiveTab] = useState<ActiveTab>('input');

  const playTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Run live validation whenever currentDfa changes
  useEffect(() => {
    let isCancelled = false;
    validateDfa(currentDfa)
      .then((val) => {
        if (!isCancelled) setValidation(val);
      })
      .catch(() => {
        if (!isCancelled) {
          const missing: { state: string; symbol: string }[] = [];
          for (const s of currentDfa.states) {
            for (const sym of currentDfa.alphabet) {
              if (!currentDfa.transitions[s]?.[sym]) {
                missing.push({ state: s, symbol: sym });
              }
            }
          }
          setValidation({
            is_valid: missing.length === 0,
            is_complete: missing.length === 0,
            errors: [],
            warnings: [],
            missing_transitions: missing,
            dead_state_candidate: 'dead',
          });
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [currentDfa]);

  // Initial load: run minimization with Table-Filling so Visualize tab is populated
  useEffect(() => {
    minimizeDfa(defaultDfa, 'table_filling')
      .then((res) => {
        setMinimizeResult(res);
        const defaultStep = Math.min(1, res.trace.length - 1);
        setCurrentStepIdx(defaultStep);
        setActiveTab('visualize');
      })
      .catch(() => {
        // Fallback: stay on input tab
      });
  }, []);

  // Minimize Handler
  const handleMinimize = useCallback(async () => {
    setIsMinimizing(true);
    setMinimizeError(null);
    try {
      const res = await minimizeDfa(currentDfa, algorithm);
      setMinimizeResult(res);
      setCurrentStepIdx(0);
      setViewMode('original');
      setActiveTab('visualize');
      setIsPlaying(false);
      setRightViewMode(algorithm === 'table_filling' ? 'table' : 'groups');
    } catch (err: any) {
      setMinimizeError(err.message || 'Failed to connect to backend minimization service.');
    } finally {
      setIsMinimizing(false);
    }
  }, [currentDfa, algorithm]);

  // Reset to default
  const handleReset = () => {
    setCurrentDfa(defaultDfa);
    setMinimizeResult(null);
    setMinimizeError(null);
    setCurrentStepIdx(0);
    setIsPlaying(false);
    setViewMode('original');
    setActiveTab('input');
  };

  // Algorithm switch handler: re-run minimize if already minimized
  const handleAlgorithmChange = (newAlgo: AlgorithmType) => {
    setAlgorithm(newAlgo);
    setRightViewMode(newAlgo === 'table_filling' ? 'table' : 'groups');
    if (minimizeResult) {
      setIsMinimizing(true);
      minimizeDfa(currentDfa, newAlgo)
        .then((res) => {
          setMinimizeResult(res);
          setCurrentStepIdx(0);
          setViewMode('original');
        })
        .catch((err) => {
          setMinimizeError(err.message || 'Minimization failed');
        })
        .finally(() => setIsMinimizing(false));
    }
  };

  // Timer Playback
  useEffect(() => {
    if (isPlaying && minimizeResult && minimizeResult.trace.length > 0) {
      playTimerRef.current = setInterval(() => {
        setCurrentStepIdx((prev) => {
          if (prev >= minimizeResult.trace.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1300 / playbackSpeed);
    } else if (playTimerRef.current) {
      clearInterval(playTimerRef.current);
    }

    return () => {
      if (playTimerRef.current) clearInterval(playTimerRef.current);
    };
  }, [isPlaying, minimizeResult, playbackSpeed]);

  const currentStep = minimizeResult?.trace[currentStepIdx] || null;
  const isFinalStep = Boolean(
    minimizeResult && currentStepIdx === minimizeResult.trace.length - 1
  );

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col font-sans text-slate-800">
      {/* 1. Slim Top Bar (δ logo + title) */}
      <TopBar />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-8 py-6 flex flex-col gap-6">
        {/* 2. Control Strip (One Card: [Table-Filling | Moore], Reset, Minimize) */}
        <ControlBar
          algorithm={algorithm}
          onAlgorithmChange={handleAlgorithmChange}
          onReset={handleReset}
          onMinimize={handleMinimize}
          isMinimizing={isMinimizing}
          canMinimize={Boolean(validation?.is_valid && validation?.is_complete)}
        />

        {/* 3. Tab Navigation (with one-line hint under each) */}
        <TabNavigation
          activeTab={activeTab}
          onTabChange={setActiveTab}
          hasMinimizedResult={Boolean(minimizeResult)}
        />

        {/* Error Banner (if any) */}
        {minimizeError && (
          <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl text-sm flex items-center justify-between shadow-sm">
            <span>{minimizeError}</span>
            <button onClick={() => setMinimizeError(null)} className="font-bold text-rose-600">×</button>
          </div>
        )}

        {/* Tab Contents */}
        <div className="flex-1">
          {/* TAB 1: INPUT */}
          {activeTab === 'input' && (
            <InputTab
              dfa={currentDfa}
              onChange={setCurrentDfa}
              onMinimize={handleMinimize}
              validation={validation}
              onResetToDefault={handleReset}
              isMinimizing={isMinimizing}
            />
          )}

          {/* TAB 2: VISUALIZE */}
          {activeTab === 'visualize' && (
            <>
              {!minimizeResult ? (
                <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm max-w-lg mx-auto">
                  <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                  <h3 className="text-lg font-bold text-slate-800">Press Minimize to begin</h3>
                  <p className="text-sm text-slate-500 mt-1.5 mb-4">
                    Run the minimization algorithm to generate and inspect the step-by-step trace and state equivalence.
                  </p>
                  <button
                    onClick={handleMinimize}
                    className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-bold transition-all shadow-sm"
                  >
                    Minimize Now
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Already Minimal Notice */}
                  {minimizeResult.is_already_minimal && (
                    <div className="p-4 bg-blue-50 border border-blue-200 text-blue-900 rounded-2xl text-sm flex items-center gap-2.5 shadow-2xs">
                      <Sparkles className="w-5 h-5 text-blue-600 flex-shrink-0" />
                      <span className="font-semibold">
                        This DFA is already minimal! All reachable states are mutually distinguishable.
                      </span>
                    </div>
                  )}

                  {/* 2-Column Visualize Layout */}
                  {currentStep && (
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
                      {/* Left: DFA Graph Card (7 cols -> 60%) */}
                      <div className="lg:col-span-7 flex flex-col">
                        <GraphCard
                          originalDfa={minimizeResult.pruned_dfa}
                          minimizedDfa={minimizeResult.minimal_dfa}
                          viewMode={viewMode}
                          onViewModeChange={setViewMode}
                          activeSplitterBlock={currentStep.highlights.splitter_block}
                          highlightedStates={currentStep.highlights.active_states}
                          unreachableStates={minimizeResult.unreachable_states}
                          activePair={currentStep.highlights.active_pair}
                          targetPair={currentStep.highlights.target_pair}
                          isFinalStep={isFinalStep}
                        />
                      </div>

                      {/* Right: Table-Filling / Groups & Step Explanation (5 cols -> 40%) */}
                      <div className="lg:col-span-5 flex flex-col gap-6">
                        {/* Segmented view switch when table filling algorithm is active */}
                        {algorithm === 'table_filling' && (
                          <div className="flex bg-slate-100 p-1 rounded-xl text-xs font-semibold text-slate-600 self-start border border-slate-200/60">
                            <button
                              onClick={() => setRightViewMode('table')}
                              className={`px-3 py-1.5 rounded-lg transition-all ${
                                rightViewMode === 'table'
                                  ? 'bg-white text-blue-600 shadow-sm font-bold'
                                  : 'text-slate-600 hover:text-slate-900'
                              }`}
                            >
                              Distinguishability Table
                            </button>
                            <button
                              onClick={() => setRightViewMode('groups')}
                              className={`px-3 py-1.5 rounded-lg transition-all ${
                                rightViewMode === 'groups'
                                  ? 'bg-white text-blue-600 shadow-sm font-bold'
                                  : 'text-slate-600 hover:text-slate-900'
                              }`}
                            >
                              Groups of States
                            </button>
                          </div>
                        )}

                        {/* Card 1: Table-Filling Grid OR Groups of States */}
                        {algorithm === 'table_filling' && rightViewMode === 'table' ? (
                          <TableFillingCard
                            states={minimizeResult.pruned_dfa.states}
                            markedPairs={currentStep.highlights.marked_pairs || []}
                            activePair={currentStep.highlights.active_pair}
                            targetPair={currentStep.highlights.target_pair}
                            markReason={currentStep.highlights.mark_reason}
                          />
                        ) : (
                          <GroupsCard
                            partition={currentStep.partition_state}
                            activeSplitterBlock={currentStep.highlights.splitter_block}
                          />
                        )}

                        {/* Card 2: Step Explanation Card */}
                        <ExplanationCard
                          stepNumber={currentStep.step_id}
                          totalSteps={currentStep.total_steps}
                          title={currentStep.title}
                          explanation={currentStep.description}
                          formalNotation={currentStep.notation}
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {/* TAB 3: TEST STRINGS */}
          {activeTab === 'test' && (
            <TestStringsTab
              originalDfa={currentDfa}
              minimizedDfa={minimizeResult?.minimal_dfa}
              hasMinimizedResult={Boolean(minimizeResult)}
            />
          )}
        </div>
      </main>

      {/* 4. Sticky Bottom Playback Bar (Active during Visualize tab) */}
      {activeTab === 'visualize' && minimizeResult && minimizeResult.trace.length > 0 && (
        <div className="sticky bottom-0 z-40">
          <PlaybackBar
            currentStep={currentStepIdx}
            totalSteps={minimizeResult.trace.length}
            isPlaying={isPlaying}
            onPlayToggle={() => setIsPlaying(!isPlaying)}
            onNext={() =>
              setCurrentStepIdx((p) => Math.min(minimizeResult.trace.length - 1, p + 1))
            }
            onPrev={() => setCurrentStepIdx((p) => Math.max(0, p - 1))}
            onSeek={(step) => setCurrentStepIdx(step)}
            speed={playbackSpeed}
            onSpeedChange={setPlaybackSpeed}
          />
        </div>
      )}
    </div>
  );
};

export default App;
