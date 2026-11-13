import React, { useState } from 'react';
import { DFADefinition, ValidationResponse } from '../../types/dfa';
import { PRESET_DFAS } from '../../presets/sampleDfas';
import { Plus, Trash2, CheckCircle2, AlertTriangle, Wand2, Edit2, RotateCcw, Sparkles } from 'lucide-react';

interface InputTabProps {
  dfa: DFADefinition;
  onChange: (updated: DFADefinition) => void;
  onMinimize: () => void;
  validation: ValidationResponse | null;
  onResetToDefault: () => void;
  isMinimizing: boolean;
}

export const InputTab: React.FC<InputTabProps> = ({
  dfa,
  onChange,
  onMinimize,
  validation,
  onResetToDefault,
  isMinimizing,
}) => {
  const [newState, setNewState] = useState('');
  const [alphabetInput, setAlphabetInput] = useState(dfa.alphabet.join(', '));
  const [editingNames, setEditingNames] = useState<Record<string, string>>({});
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Missing transitions check
  const missingTransitions = validation?.missing_transitions || [];
  const isComplete = validation ? validation.is_complete : true;
  const isValid = validation ? validation.is_valid : true;

  // Next available state name generator
  const getNextAvailableStateName = (): string => {
    const singleLetters = dfa.states.filter((s) => /^[A-Z]$/.test(s));
    if (singleLetters.length > 0) {
      for (let charCode = 65; charCode <= 90; charCode++) {
        const letter = String.fromCharCode(charCode);
        if (!dfa.states.includes(letter)) return letter;
      }
    }
    const qMatches = dfa.states
      .map((s) => {
        const m = s.match(/^q(\d+)$/i);
        return m ? parseInt(m[1], 10) : -1;
      })
      .filter((n) => n >= 0);
    if (qMatches.length > 0) {
      const maxQ = Math.max(...qMatches);
      return `q${maxQ + 1}`;
    }
    let count = dfa.states.length;
    while (dfa.states.includes(`q${count}`)) {
      count++;
    }
    return `q${count}`;
  };

  // Add dead state
  const handleAddDeadState = () => {
    const deadName = validation?.dead_state_candidate || 'dead';
    const states = [...dfa.states];
    if (!states.includes(deadName)) {
      states.push(deadName);
    }

    const transitions = JSON.parse(JSON.stringify(dfa.transitions));
    if (!transitions[deadName]) {
      transitions[deadName] = {};
    }
    for (const sym of dfa.alphabet) {
      transitions[deadName][sym] = deadName;
    }

    // Fill missing transitions
    for (const s of dfa.states) {
      if (!transitions[s]) transitions[s] = {};
      for (const sym of dfa.alphabet) {
        if (!transitions[s][sym]) {
          transitions[s][sym] = deadName;
        }
      }
    }

    onChange({
      ...dfa,
      states,
      transitions,
    });
    setSuccessMsg(`Added dead state "${deadName}" and filled all missing transitions.`);
    setTimeout(() => setSuccessMsg(null), 3000);
  };

  // State toggle accepting
  const handleStateToggleAccept = (state: string) => {
    const accept = dfa.accept_states.includes(state)
      ? dfa.accept_states.filter((s) => s !== state)
      : [...dfa.accept_states, state];
    onChange({ ...dfa, accept_states: accept });
  };

  // Set start state
  const handleSetStart = (state: string) => {
    onChange({ ...dfa, start_state: state });
  };

  // Transition change
  const handleTransitionChange = (fromState: string, symbol: string, toState: string) => {
    const transitions = JSON.parse(JSON.stringify(dfa.transitions));
    if (!transitions[fromState]) transitions[fromState] = {};
    transitions[fromState][symbol] = toState;
    onChange({ ...dfa, transitions });
  };

  // Quick preset loader helper
  const handleLoadPreset = (presetKey: string) => {
    const preset = PRESET_DFAS[presetKey];
    if (preset) {
      onChange(preset.dfa);
      setAlphabetInput(preset.dfa.alphabet.join(', '));
      setSuccessMsg(`Loaded "${preset.name}".`);
      setTimeout(() => setSuccessMsg(null), 2500);
    }
  };

  // ADD STATE
  const handleAddState = () => {
    let name = newState.trim();
    if (!name) {
      name = getNextAvailableStateName();
    }

    if (dfa.states.includes(name)) {
      setErrorMsg(`State "${name}" already exists! Please choose another name.`);
      return;
    }

    setErrorMsg(null);
    const states = [...dfa.states, name];
    const transitions = JSON.parse(JSON.stringify(dfa.transitions));
    transitions[name] = {};
    for (const sym of dfa.alphabet) {
      transitions[name][sym] = name;
    }

    onChange({ ...dfa, states, transitions });
    setNewState('');
    setSuccessMsg(`State "${name}" added.`);
    setTimeout(() => setSuccessMsg(null), 2500);
  };

  // RENAME STATE
  const handleCommitRename = (oldState: string) => {
    const candidate = editingNames[oldState];
    if (candidate === undefined) return;

    const newName = candidate.trim();

    if (!newName || newName === oldState) {
      const updated = { ...editingNames };
      delete updated[oldState];
      setEditingNames(updated);
      return;
    }

    if (dfa.states.includes(newName)) {
      setErrorMsg(`Cannot rename to "${newName}": state already exists!`);
      const updated = { ...editingNames };
      delete updated[oldState];
      setEditingNames(updated);
      return;
    }

    setErrorMsg(null);

    const states = dfa.states.map((s) => (s === oldState ? newName : s));
    const start_state = dfa.start_state === oldState ? newName : dfa.start_state;
    const accept_states = dfa.accept_states.map((s) => (s === oldState ? newName : s));

    const transitions: Record<string, Record<string, string>> = {};
    for (const s of dfa.states) {
      const sourceKey = s === oldState ? newName : s;
      transitions[sourceKey] = {};
      for (const sym of dfa.alphabet) {
        const dest = dfa.transitions[s]?.[sym];
        transitions[sourceKey][sym] = dest === oldState ? newName : dest;
      }
    }

    const updated = { ...editingNames };
    delete updated[oldState];
    setEditingNames(updated);

    onChange({
      states,
      alphabet: dfa.alphabet,
      start_state,
      accept_states,
      transitions,
    });

    setSuccessMsg(`Renamed state "${oldState}" to "${newName}".`);
    setTimeout(() => setSuccessMsg(null), 2500);
  };

  // REMOVE STATE
  const handleRemoveState = (stateToRemove: string) => {
    if (dfa.states.length <= 1) {
      setErrorMsg('Cannot remove the last remaining state.');
      return;
    }
    setErrorMsg(null);

    const states = dfa.states.filter((s) => s !== stateToRemove);
    const accept_states = dfa.accept_states.filter((s) => s !== stateToRemove);
    const start_state = dfa.start_state === stateToRemove ? states[0] : dfa.start_state;

    const transitions: Record<string, Record<string, string>> = {};
    for (const s of states) {
      transitions[s] = {};
      for (const sym of dfa.alphabet) {
        const dest = dfa.transitions[s]?.[sym];
        transitions[s][sym] = dest === stateToRemove ? start_state : dest || start_state;
      }
    }

    onChange({
      states,
      alphabet: dfa.alphabet,
      start_state,
      accept_states,
      transitions,
    });

    setSuccessMsg(`State "${stateToRemove}" removed.`);
    setTimeout(() => setSuccessMsg(null), 2500);
  };

  // ALPHABET EDIT
  const handleAlphabetBlur = () => {
    const rawTokens = alphabetInput
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    const newAlpha = Array.from(new Set(rawTokens));
    if (newAlpha.length === 0) {
      setErrorMsg('Alphabet must contain at least one symbol.');
      setAlphabetInput(dfa.alphabet.join(', '));
      return;
    }

    setErrorMsg(null);
    const transitions: Record<string, Record<string, string>> = {};
    for (const s of dfa.states) {
      transitions[s] = {};
      for (const sym of newAlpha) {
        transitions[s][sym] = dfa.transitions[s]?.[sym] || s;
      }
    }

    onChange({
      ...dfa,
      alphabet: newAlpha,
      transitions,
    });
    setAlphabetInput(newAlpha.join(', '));
    setSuccessMsg(`Alphabet updated to: ${newAlpha.join(', ')}`);
    setTimeout(() => setSuccessMsg(null), 2500);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Transition Table Card */}
      <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-7 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
          <div>
            <h3 className="text-lg font-bold text-slate-800 tracking-tight">Transition Table (δ)</h3>
            <p className="text-sm text-slate-500 mt-0.5">
              Edit state names directly in the table, set start/accepting states, and define transitions.
            </p>
          </div>
          <div className="flex items-center gap-2">
            {!isComplete && (
              <button
                onClick={handleAddDeadState}
                className="flex items-center gap-1.5 px-4 py-2 bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-300 rounded-xl text-xs font-bold transition-colors shadow-2xs"
              >
                <Wand2 className="w-3.5 h-3.5" />
                <span>Autofill Dead State</span>
              </button>
            )}
          </div>
        </div>

        {/* Feedback Alerts */}
        {errorMsg && (
          <div className="mb-4 p-3.5 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-sm flex items-center justify-between">
            <span>{errorMsg}</span>
            <button onClick={() => setErrorMsg(null)} className="text-rose-600 font-bold ml-2">×</button>
          </div>
        )}
        {successMsg && (
          <div className="mb-4 p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-sm flex items-center justify-between">
            <span>{successMsg}</span>
            <button onClick={() => setSuccessMsg(null)} className="text-emerald-600 font-bold ml-2">×</button>
          </div>
        )}

        {/* Table */}
        <div className="overflow-x-auto border border-slate-200 rounded-xl">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-xs">
              <tr>
                <th className="px-4 py-3.5">State (Click to Rename)</th>
                <th className="px-4 py-3.5 text-center">Start</th>
                <th className="px-4 py-3.5 text-center">Accepting</th>
                {dfa.alphabet.map((sym) => (
                  <th key={sym} className="px-4 py-3.5 text-center">
                    Input '{sym}'
                  </th>
                ))}
                <th className="px-4 py-3.5 text-center">Delete</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {dfa.states.map((s) => {
                const isStart = dfa.start_state === s;
                const isAccept = dfa.accept_states.includes(s);
                const currentNameValue = editingNames[s] !== undefined ? editingNames[s] : s;

                return (
                  <tr key={s} className="hover:bg-slate-50/70 transition-colors">
                    {/* Editable State Name Cell */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={currentNameValue}
                          onChange={(e) => setEditingNames({ ...editingNames, [s]: e.target.value })}
                          onBlur={() => handleCommitRename(s)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleCommitRename(s);
                            if (e.key === 'Escape') {
                              const updated = { ...editingNames };
                              delete updated[s];
                              setEditingNames(updated);
                            }
                          }}
                          className="w-24 px-2.5 py-1 text-sm font-mono font-bold text-slate-800 bg-slate-50 border border-slate-200 rounded-lg hover:border-slate-300 focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all shadow-2xs"
                          title="Click to rename state, press Enter to save"
                        />
                        <Edit2 className="w-3.5 h-3.5 text-slate-400 opacity-60" />
                      </div>
                    </td>

                    <td className="px-4 py-3 text-center">
                      <input
                        type="radio"
                        name="start_state_radio"
                        checked={isStart}
                        onChange={() => handleSetStart(s)}
                        className="w-4 h-4 text-blue-600 focus:ring-blue-500 cursor-pointer"
                        title="Set as start state"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="checkbox"
                        checked={isAccept}
                        onChange={() => handleStateToggleAccept(s)}
                        className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 cursor-pointer"
                        title="Toggle accepting status"
                      />
                    </td>
                    {dfa.alphabet.map((sym) => {
                      const currentDest = dfa.transitions[s]?.[sym] || '';
                      return (
                        <td key={sym} className="px-4 py-3 text-center">
                          <select
                            value={currentDest}
                            onChange={(e) => handleTransitionChange(s, sym, e.target.value)}
                            className="px-3 py-1.5 text-sm border border-slate-200 rounded-lg bg-white font-mono font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-2xs"
                          >
                            <option value="">--</option>
                            {dfa.states.map((dest) => (
                              <option key={dest} value={dest}>
                                {dest}
                              </option>
                            ))}
                          </select>
                        </td>
                      );
                    })}
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => handleRemoveState(s)}
                        disabled={dfa.states.length <= 1}
                        className="text-slate-400 hover:text-red-600 disabled:opacity-20 transition-colors p-1"
                        title="Delete state"
                      >
                        <Trash2 className="w-4 h-4 mx-auto" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Add State Row */}
        <div className="flex flex-wrap items-center gap-3.5 mt-5 pt-4 border-t border-slate-100">
          <input
            type="text"
            placeholder={`State name (leave blank for "${getNextAvailableStateName()}")`}
            value={newState}
            onChange={(e) => setNewState(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAddState()}
            className="px-4 py-2.5 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 w-80 shadow-2xs"
          />
          <button
            onClick={handleAddState}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>Add State</span>
          </button>
          <span className="text-xs text-slate-400">
            Tip: Press Enter or leave blank to auto-name.
          </span>
        </div>
      </div>

      {/* Validation & Overview Card */}
      <div className="space-y-6">
        {/* Quick Starter DFA Presets */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <h4 className="text-sm font-bold text-slate-800">Quick Starter DFAs</h4>
          </div>
          <p className="text-xs text-slate-500 mb-3">
            Want to test an interesting DFA right away? Click any preset:
          </p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleLoadPreset('textbook')}
              className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 transition-colors"
            >
              Textbook (6 states)
            </button>
            <button
              onClick={() => handleLoadPreset('minimal')}
              className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 transition-colors"
            >
              Already Minimal
            </button>
            <button
              onClick={() => handleLoadPreset('unreachable')}
              className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 transition-colors"
            >
              Unreachable States
            </button>
            <button
              onClick={() => handleLoadPreset('divisible3')}
              className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 transition-colors"
            >
              Divisible by 3
            </button>
          </div>
        </div>

        {/* DFA Summary Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h3 className="text-base font-bold text-slate-800 mb-3">DFA Summary</h3>
          <div className="space-y-3.5 text-sm">
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">States count:</span>
              <span className="font-bold text-slate-800">{dfa.states.length}</span>
            </div>

            {/* Editable Alphabet */}
            <div className="py-1.5 border-b border-slate-100">
              <div className="flex justify-between items-center mb-1.5">
                <span className="text-slate-500">Alphabet (Σ):</span>
                <span className="text-xs text-slate-400 font-sans">comma-separated</span>
              </div>
              <input
                type="text"
                value={alphabetInput}
                onChange={(e) => setAlphabetInput(e.target.value)}
                onBlur={handleAlphabetBlur}
                className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg font-mono font-bold text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-2xs"
              />
            </div>

            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Start State:</span>
              <span className="font-mono font-bold text-blue-600">{dfa.start_state}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Accepting:</span>
              <span className="font-mono font-bold text-amber-700">
                {dfa.accept_states.join(', ') || 'None'}
              </span>
            </div>
          </div>

          {/* Validation Status */}
          <div className="mt-6 pt-4 border-t border-slate-100">
            {isComplete && isValid ? (
              <div className="flex items-center gap-2 text-emerald-600 text-sm font-semibold">
                <CheckCircle2 className="w-4 h-4" />
                <span>Complete Deterministic DFA (ready)</span>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-amber-600 text-sm font-semibold">
                  <AlertTriangle className="w-4 h-4" />
                  <span>{missingTransitions.length} missing transition(s)</span>
                </div>
                {validation?.errors && validation.errors.length > 0 && (
                  <ul className="text-xs text-rose-600 list-disc list-inside">
                    {validation.errors.map((err, i) => (
                      <li key={i}>{err}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>

          <div className="mt-6 space-y-2.5">
            <button
              onClick={onMinimize}
              disabled={isMinimizing || !isValid || !isComplete}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl text-sm font-bold transition-all shadow-sm flex items-center justify-center gap-2"
            >
              {isMinimizing ? 'Minimizing...' : 'Run Minimization'}
            </button>

            <button
              onClick={onResetToDefault}
              className="w-full py-2.5 border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-4 h-4 text-slate-400" />
              <span>Reset to Default Textbook DFA</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
