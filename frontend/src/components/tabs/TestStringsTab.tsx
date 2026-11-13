import React, { useState } from 'react';
import { DFADefinition, SimulateResponse } from '../../types/dfa';
import { simulateDfa } from '../../services/api';
import { Play, CheckCircle2, XCircle, AlertCircle, ChevronRight, RotateCcw } from 'lucide-react';

interface TestStringsTabProps {
  originalDfa: DFADefinition;
  minimizedDfa?: DFADefinition;
  hasMinimizedResult: boolean;
}

export const TestStringsTab: React.FC<TestStringsTabProps> = ({
  originalDfa,
  minimizedDfa,
  hasMinimizedResult,
}) => {
  const [singleInput, setSingleInput] = useState('0101');
  const [singleResult, setSingleResult] = useState<SimulateResponse | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  // Interactive String Step Stepper
  const [stepIdx, setStepIdx] = useState<number>(0);
  const [isStepping, setIsStepping] = useState<boolean>(false);

  // Batch testing
  const [batchInputText, setBatchInputText] = useState("0\n1\n00\n01\n10\n11\n0101\n1010\n");
  const [batchResults, setBatchResults] = useState<SimulateResponse[]>([]);
  const [isBatchRunning, setIsBatchRunning] = useState(false);

  const sampleChips = ['', '0', '1', '01', '0101', '1010', '0011'];

  // Run single string
  const handleRunSingle = async (inputStr: string = singleInput) => {
    setIsSimulating(true);
    setSingleInput(inputStr);
    try {
      const res = await simulateDfa(originalDfa, minimizedDfa, inputStr);
      setSingleResult(res);
      setStepIdx(0);
      setIsStepping(false);
    } catch (err: any) {
      alert(err.message || 'Simulation error');
    } finally {
      setIsSimulating(false);
    }
  };

  // Run batch strings
  const handleRunBatch = async () => {
    setIsBatchRunning(true);
    const lines = batchInputText
      .split('\n')
      .map((l) => l.trim());

    const results: SimulateResponse[] = [];
    for (const line of lines) {
      if (line === '' && lines.length > 1 && results.length > 0) continue;
      try {
        const res = await simulateDfa(originalDfa, minimizedDfa, line);
        results.push(res);
      } catch {
        // ignore
      }
    }
    setBatchResults(results);
    setIsBatchRunning(false);
  };

  if (!hasMinimizedResult) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm max-w-lg mx-auto">
        <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-slate-800">Press Minimize to begin</h3>
        <p className="text-sm text-slate-500 mt-1.5">
          Once you run the minimization algorithm, you can test input strings here and verify equivalence between both DFAs.
        </p>
      </div>
    );
  }

  const origPath = singleResult?.original_result.path || [];
  const minPath = singleResult?.minimized_result?.path || [];

  return (
    <div className="space-y-6">
      {/* Interactive Single String Tester */}
      <div className="bg-white rounded-2xl border border-slate-200 p-7 shadow-sm">
        <h3 className="text-lg font-bold text-slate-800 tracking-tight">
          Single String Interactive Simulation
        </h3>
        <p className="text-sm text-slate-500 mt-0.5 mb-4">
          Runs on both Original and Minimized DFA via backend <code className="bg-slate-100 px-1.5 py-0.5 rounded font-mono text-xs">POST /api/simulate</code> to verify transition paths and equivalence.
        </p>

        {/* Quick Test Chips */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <span className="text-xs font-semibold text-slate-500">Quick Test Strings:</span>
          {sampleChips.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleRunSingle(chip)}
              className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded-lg text-xs font-mono font-semibold text-slate-700 transition-colors"
            >
              {chip === '' ? 'ε (empty)' : chip}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-3 max-w-md">
          <input
            type="text"
            value={singleInput}
            onChange={(e) => setSingleInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRunSingle()}
            placeholder="Enter string (leave blank for ε)"
            className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-mono font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-2xs"
          />
          <button
            onClick={() => handleRunSingle()}
            disabled={isSimulating}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl text-sm font-bold transition-all shadow-sm flex items-center gap-2 active:scale-95"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>{isSimulating ? 'Testing...' : 'Test String'}</span>
          </button>
        </div>

        {/* Invalid Alphabet Error Alert */}
        {singleResult && !singleResult.is_valid_alphabet && (
          <div className="mt-4 p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-sm flex items-center gap-2.5">
            <XCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span>{singleResult.alphabet_error}</span>
          </div>
        )}

        {/* Interactive Tracing Execution View */}
        {singleResult && singleResult.is_valid_alphabet && (
          <div className="space-y-4 mt-6">
            {/* Step-by-Step String Tape Runner */}
            {singleInput.length > 0 && (
              <div className="p-4 bg-blue-50/60 border border-blue-200 rounded-xl flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-bold text-blue-900 uppercase tracking-wider">String Tape:</span>
                  <div className="flex items-center gap-1 font-mono text-base">
                    {singleInput.split('').map((char, i) => (
                      <span
                        key={i}
                        className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold border transition-all ${
                          isStepping && i === stepIdx - 1
                            ? 'bg-blue-600 text-white border-blue-700 shadow-sm scale-110'
                            : i < stepIdx
                            ? 'bg-blue-100 text-blue-800 border-blue-300'
                            : 'bg-white text-slate-700 border-slate-200'
                        }`}
                      >
                        {char}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      setIsStepping(true);
                      setStepIdx((prev) => Math.min(origPath.length - 1, prev + 1));
                    }}
                    disabled={stepIdx >= origPath.length - 1}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-blue-200 rounded-lg text-xs font-bold text-blue-700 hover:bg-blue-50 disabled:opacity-40 transition-all shadow-2xs"
                  >
                    <span>Step Tape</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => {
                      setStepIdx(0);
                      setIsStepping(false);
                    }}
                    className="p-1.5 text-slate-400 hover:text-slate-700 rounded transition-colors"
                    title="Reset stepper"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {/* Path Grids */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Original DFA Execution */}
              <div className="border border-slate-200 rounded-xl p-5 bg-slate-50/60">
                <div className="flex items-center justify-between mb-3.5">
                  <span className="text-sm font-bold text-slate-800">Original DFA Execution</span>
                  {singleResult.original_result.accepted ? (
                    <span className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-100 px-3 py-1 rounded-full">
                      <CheckCircle2 className="w-4 h-4" /> Accepted
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 text-xs font-bold text-rose-700 bg-rose-100 px-3 py-1 rounded-full">
                      <XCircle className="w-4 h-4" /> Rejected
                    </span>
                  )}
                </div>

                <div className="space-y-2 font-mono">
                  <div className="text-slate-500 text-xs font-sans">State Sequence:</div>
                  <div className="flex flex-wrap items-center gap-2">
                    {origPath.map((state, idx) => (
                      <React.Fragment key={idx}>
                        <span
                          className={`px-3 py-1 rounded-lg font-bold text-sm border transition-all ${
                            isStepping && idx === stepIdx
                              ? 'bg-blue-600 text-white border-blue-700 shadow-md ring-2 ring-blue-300'
                              : 'bg-white border-slate-200 text-slate-800'
                          }`}
                        >
                          {state}
                        </span>
                        {idx < origPath.length - 1 && (
                          <span className="text-slate-400 font-sans text-xs">
                            —({singleInput[idx]})→
                          </span>
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              </div>

              {/* Minimized DFA Execution */}
              <div className="border border-slate-200 rounded-xl p-5 bg-slate-50/60">
                <div className="flex items-center justify-between mb-3.5">
                  <span className="text-sm font-bold text-slate-800">Minimized DFA Execution</span>
                  {singleResult.minimized_result ? (
                    singleResult.minimized_result.accepted ? (
                      <span className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-100 px-3 py-1 rounded-full">
                        <CheckCircle2 className="w-4 h-4" /> Accepted
                      </span>
                    ) : (
                      <span className="flex items-center gap-1.5 text-xs font-bold text-rose-700 bg-rose-100 px-3 py-1 rounded-full">
                        <XCircle className="w-4 h-4" /> Rejected
                      </span>
                    )
                  ) : (
                    <span className="text-xs text-slate-400">No minimized result</span>
                  )}
                </div>

                {singleResult.minimized_result && (
                  <div className="space-y-2 font-mono">
                    <div className="text-slate-500 text-xs font-sans">State Sequence:</div>
                    <div className="flex flex-wrap items-center gap-2">
                      {minPath.map((state, idx) => (
                        <React.Fragment key={idx}>
                          <span
                            className={`px-3 py-1 rounded-lg font-bold text-sm border transition-all ${
                              isStepping && idx === stepIdx
                                ? 'bg-blue-600 text-white border-blue-700 shadow-md ring-2 ring-blue-300'
                                : 'bg-white border-slate-200 text-slate-800'
                            }`}
                          >
                            {state}
                          </span>
                          {idx < minPath.length - 1 && (
                            <span className="text-slate-400 font-sans text-xs">
                              —({singleInput[idx]})→
                            </span>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Equivalence Confirmation Banner */}
            <div className="p-4 bg-emerald-50/70 border border-emerald-200 rounded-xl flex items-center justify-between text-sm">
              <span className="text-slate-700 font-medium">Equivalence Result:</span>
              {singleResult.agreement ? (
                <span className="font-bold text-emerald-700 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Original and Minimized DFA Produce Identical Outputs (Agreement Verified)
                </span>
              ) : (
                <span className="font-bold text-rose-600 flex items-center gap-1.5">
                  <XCircle className="w-4 h-4 text-rose-600" /> Outputs Differ!
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Batch String Testing Suite */}
      <div className="bg-white rounded-2xl border border-slate-200 p-7 shadow-sm">
        <h3 className="text-lg font-bold text-slate-800 tracking-tight mb-1">
          Batch String Verification Suite
        </h3>
        <p className="text-sm text-slate-500 mb-4">
          Enter multiple test strings (one per line) to verify agreement across a batch test suite.
        </p>

        <div className="flex flex-col gap-3 max-w-lg mb-4">
          <textarea
            rows={4}
            value={batchInputText}
            onChange={(e) => setBatchInputText(e.target.value)}
            className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-2xs"
            placeholder="one string per line..."
          />
          <button
            onClick={handleRunBatch}
            disabled={isBatchRunning}
            className="self-start px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-bold transition-all shadow-sm active:scale-95"
          >
            {isBatchRunning ? 'Running Batch...' : 'Run Batch Suite'}
          </button>
        </div>

        {batchResults.length > 0 && (
          <div className="border border-slate-200 rounded-xl overflow-hidden mt-4">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-xs">
                <tr>
                  <th className="px-5 py-3">Input String</th>
                  <th className="px-5 py-3">Original DFA</th>
                  <th className="px-5 py-3">Minimized DFA</th>
                  <th className="px-5 py-3 text-center">Agreement</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {batchResults.map((res, i) => (
                  <tr key={i} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-5 py-3 font-bold text-slate-800">
                      {res.input_string === '' ? 'ε (empty string)' : res.input_string}
                    </td>
                    <td className="px-5 py-3">
                      <span
                        className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                          res.original_result.accepted
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {res.original_result.accepted ? 'ACCEPT' : 'REJECT'}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      {res.minimized_result ? (
                        <span
                          className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                            res.minimized_result.accepted
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-rose-100 text-rose-800'
                          }`}
                        >
                          {res.minimized_result.accepted ? 'ACCEPT' : 'REJECT'}
                        </span>
                      ) : (
                        <span className="text-slate-400 font-sans">--</span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-center font-sans">
                      {res.agreement ? (
                        <span className="text-emerald-600 font-bold text-sm">✓ Match</span>
                      ) : (
                        <span className="text-rose-600 font-bold text-sm">✗ Mismatch</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
