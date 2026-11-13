import React from 'react';
import { AlgorithmType } from '../../types/dfa';
import { RotateCcw, Zap } from 'lucide-react';

interface ControlBarProps {
  algorithm: AlgorithmType;
  onAlgorithmChange: (algo: AlgorithmType) => void;
  onReset: () => void;
  onMinimize: () => void;
  isMinimizing?: boolean;
  canMinimize?: boolean;
}

export const ControlBar: React.FC<ControlBarProps> = ({
  algorithm,
  onAlgorithmChange,
  onReset,
  onMinimize,
  isMinimizing = false,
  canMinimize = true,
}) => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 px-7 py-4 shadow-sm flex flex-wrap items-center justify-between gap-4 select-none">
      {/* Left: Algorithm segmented switch [ Table-Filling | Moore ] */}
      <div className="flex items-center gap-4">
        <span className="text-sm font-semibold text-slate-700">Algorithm:</span>
        <div className="flex bg-slate-100 p-1.5 rounded-xl text-sm font-semibold text-slate-600 border border-slate-200/60">
          <button
            onClick={() => onAlgorithmChange('table_filling')}
            className={`px-4 py-2 rounded-lg transition-all ${
              algorithm === 'table_filling'
                ? 'bg-white text-blue-600 shadow-sm font-bold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            title="Table-Filling Method (Myhill-Nerode): Triangular pair distinguishability table"
          >
            Table-Filling
          </button>
          <button
            onClick={() => onAlgorithmChange('moore')}
            className={`px-4 py-2 rounded-lg transition-all ${
              algorithm === 'moore'
                ? 'bg-white text-blue-600 shadow-sm font-bold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            title="Moore's Algorithm: Iterative k-equivalence signatures until stable"
          >
            Moore
          </button>
        </div>
      </div>

      {/* Right: Reset and Minimize Buttons */}
      <div className="flex items-center gap-3.5">
        <button
          onClick={onReset}
          className="flex items-center gap-2 px-5 py-2.5 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-all shadow-sm active:scale-95"
          title="Restore default textbook DFA and clear results"
        >
          <RotateCcw className="w-4 h-4 text-slate-400" />
          <span>Reset</span>
        </button>

        <button
          onClick={onMinimize}
          disabled={isMinimizing || !canMinimize}
          className="flex items-center gap-2 px-7 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl text-sm font-bold transition-all shadow-sm active:scale-95 hover:shadow-md"
          title={canMinimize ? 'Run minimization algorithm' : 'Please resolve missing transitions in Input tab first'}
        >
          {isMinimizing ? (
            <>
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Minimizing...</span>
            </>
          ) : (
            <>
              <Zap className="w-4 h-4 fill-current" />
              <span>Minimize</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
