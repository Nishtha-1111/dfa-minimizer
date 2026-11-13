import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TableFillingCardProps {
  states: string[];
  markedPairs: string[][];
  activePair?: string[];
  targetPair?: string[];
  markReason?: string;
}

export const TableFillingCard: React.FC<TableFillingCardProps> = ({
  states,
  markedPairs = [],
  activePair = [],
  targetPair = [],
  markReason,
}) => {
  const sortedStates = [...states].sort();
  const n = sortedStates.length;

  const isMarked = (p: string, q: string) => {
    return markedPairs.some(
      ([u, v]) => (u === p && v === q) || (u === q && v === p)
    );
  };

  const isActive = (p: string, q: string) => {
    if (!activePair || activePair.length < 2) return false;
    return (
      (activePair[0] === p && activePair[1] === q) ||
      (activePair[0] === q && activePair[1] === p)
    );
  };

  const isTarget = (p: string, q: string) => {
    if (!targetPair || targetPair.length < 2) return false;
    return (
      (targetPair[0] === p && targetPair[1] === q) ||
      (targetPair[0] === q && targetPair[1] === p)
    );
  };

  // If DFA has <= 1 state, table filling is trivial
  if (n <= 1) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 text-center text-sm text-slate-500">
        Table-filling requires at least 2 states.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between select-none">
      <div>
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-lg font-bold text-slate-800 tracking-tight">
            Distinguishability Table
          </h3>
          <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
            Myhill-Nerode
          </span>
        </div>
        <p className="text-sm text-slate-500 mb-4">
          Unmarked cells indicate equivalent states that merge together.
        </p>

        {/* Lower Triangular Grid */}
        <div className="overflow-x-auto pb-2">
          <table className="border-collapse mx-auto">
            <tbody>
              {/* Rows from state index 1 to n-1 */}
              {sortedStates.slice(1).map((rowState, rowIdx) => {
                const actualRowIdx = rowIdx + 1;
                return (
                  <tr key={`row-${rowState}`}>
                    {/* Row Header */}
                    <td className="px-2.5 py-1.5 font-mono font-bold text-sm text-slate-700 border-r-2 border-slate-300 text-center w-8">
                      {rowState}
                    </td>

                    {/* Columns up to row index */}
                    {sortedStates.slice(0, actualRowIdx).map((colState) => {
                      const marked = isMarked(rowState, colState);
                      const active = isActive(rowState, colState);
                      const target = isTarget(rowState, colState);

                      let bgClass = 'bg-slate-50/60 border-slate-200 text-slate-400';
                      if (active) {
                        bgClass = 'bg-amber-100 border-amber-400 text-amber-900 ring-2 ring-amber-400 font-bold';
                      } else if (target) {
                        bgClass = 'bg-blue-100 border-blue-400 text-blue-900 font-bold';
                      } else if (marked) {
                        bgClass = 'bg-rose-50/70 border-rose-200 text-rose-600 font-bold';
                      }

                      return (
                        <td
                          key={`cell-${rowState}-${colState}`}
                          className={`w-9 h-9 border text-center text-sm transition-all duration-200 ${bgClass}`}
                          title={`Pair (${colState}, ${rowState})${marked ? ': Marked (Distinguished)' : ': Unmarked'}`}
                        >
                          <AnimatePresence mode="wait">
                            {marked ? (
                              <motion.span
                                key="marked-x"
                                initial={{ scale: 0, rotate: -45 }}
                                animate={{ scale: 1, rotate: 0 }}
                                transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                                className="inline-block font-sans font-black"
                              >
                                ✕
                              </motion.span>
                            ) : (
                              <span className="opacity-0 font-sans">•</span>
                            )}
                          </AnimatePresence>
                        </td>
                      );
                    })}
                  </tr>
                );
              })}

              {/* Bottom Column Headers (states 0 to n-2) */}
              <tr>
                <td className="w-8"></td>
                {sortedStates.slice(0, n - 1).map((colState) => (
                  <td
                    key={`col-header-${colState}`}
                    className="pt-2 text-center font-mono font-bold text-sm text-slate-700 border-t-2 border-slate-300 w-9"
                  >
                    {colState}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>

        {/* Active Mark Reason banner */}
        {markReason && (
          <div className="mt-3.5 p-3 bg-amber-50/80 border border-amber-200 rounded-xl text-xs text-amber-950 leading-relaxed font-medium">
            <span className="font-bold text-amber-800">Observation: </span>
            {markReason}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-medium">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-4 h-4 bg-rose-50 border border-rose-300 text-rose-600 text-center font-bold text-[10px] leading-4 rounded">
              ✕
            </span>
            Distinguished
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-4 h-4 bg-slate-50 border border-slate-200 text-center rounded"></span>
            Equivalent
          </span>
        </div>
        <span className="text-[11px] text-slate-400">
          {markedPairs.length} of {(n * (n - 1)) / 2} pairs marked
        </span>
      </div>
    </div>
  );
};
