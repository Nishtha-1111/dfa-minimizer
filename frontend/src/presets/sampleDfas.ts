import { DFADefinition } from '../types/dfa';

export interface PresetDFA {
  id: string;
  name: string;
  description: string;
  dfa: DFADefinition;
  layout?: Record<string, { x: number; y: number }>;
}

export const PRESET_DFAS: Record<string, PresetDFA> = {
  textbook: {
    id: 'textbook',
    name: 'Textbook (equivalent states)',
    description: 'Classic 6-state DFA where {A, B}, {C, D}, and {E, F} merge into 3 equivalent states.',
    dfa: {
      states: ['A', 'B', 'C', 'D', 'E', 'F'],
      alphabet: ['0', '1'],
      start_state: 'A',
      accept_states: ['C', 'D'],
      transitions: {
        A: { '0': 'B', '1': 'C' },
        B: { '0': 'A', '1': 'D' },
        C: { '0': 'E', '1': 'E' },
        D: { '0': 'F', '1': 'E' },
        E: { '0': 'E', '1': 'F' },
        F: { '0': 'F', '1': 'F' },
      },
    },
    layout: {
      A: { x: 130, y: 260 },
      B: { x: 240, y: 150 },
      C: { x: 240, y: 370 },
      D: { x: 400, y: 150 },
      E: { x: 400, y: 370 },
      F: { x: 520, y: 260 },
    },
  },
  minimal: {
    id: 'minimal',
    name: 'Already Minimal DFA',
    description: 'A 4-state DFA accepting strings with an even number of 0s and 1s; cannot be reduced further.',
    dfa: {
      states: ['q0', 'q1', 'q2', 'q3'],
      alphabet: ['0', '1'],
      start_state: 'q0',
      accept_states: ['q0'],
      transitions: {
        q0: { '0': 'q1', '1': 'q2' },
        q1: { '0': 'q0', '1': 'q3' },
        q2: { '0': 'q3', '1': 'q0' },
        q3: { '0': 'q2', '1': 'q1' },
      },
    },
  },
  unreachable: {
    id: 'unreachable',
    name: 'DFA with Unreachable States',
    description: 'Contains states unreachable from start state that must be pruned in Phase 1.',
    dfa: {
      states: ['q0', 'q1', 'q2', 'q3', 'u1', 'u2'],
      alphabet: ['0', '1'],
      start_state: 'q0',
      accept_states: ['q2', 'u2'],
      transitions: {
        q0: { '0': 'q1', '1': 'q0' },
        q1: { '0': 'q1', '1': 'q2' },
        q2: { '0': 'q0', '1': 'q2' },
        q3: { '0': 'q2', '1': 'q1' },
        u1: { '0': 'u2', '1': 'q0' },
        u2: { '0': 'u1', '1': 'u2' },
      },
    },
  },
  divisible3: {
    id: 'divisible3',
    name: 'Binary Divisible by 3',
    description: 'DFA recognizing binary numbers divisible by 3.',
    dfa: {
      states: ['rem0', 'rem1', 'rem2'],
      alphabet: ['0', '1'],
      start_state: 'rem0',
      accept_states: ['rem0'],
      transitions: {
        rem0: { '0': 'rem0', '1': 'rem1' },
        rem1: { '0': 'rem2', '1': 'rem0' },
        rem2: { '0': 'rem1', '1': 'rem2' },
      },
    },
  },
  all_merge: {
    id: 'all_merge',
    name: 'All States Merge',
    description: 'All reachable states are equivalent and merge into a single universal state.',
    dfa: {
      states: ['s1', 's2', 's3', 's4'],
      alphabet: ['a', 'b'],
      start_state: 's1',
      accept_states: ['s1', 's2', 's3', 's4'],
      transitions: {
        s1: { a: 's2', b: 's3' },
        s2: { a: 's3', b: 's4' },
        s3: { a: 's4', b: 's1' },
        s4: { a: 's1', b: 's2' },
      },
    },
  },
  complex8: {
    id: 'complex8',
    name: '8-State Complex DFA',
    description: 'Larger 8-state DFA suitable for demonstrating non-trivial step-by-step partition refinement.',
    dfa: {
      states: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
      alphabet: ['0', '1'],
      start_state: 'A',
      accept_states: ['C', 'G'],
      transitions: {
        A: { '0': 'B', '1': 'F' },
        B: { '0': 'A', '1': 'C' },
        C: { '0': 'G', '1': 'D' },
        D: { '0': 'E', '1': 'H' },
        E: { '0': 'H', '1': 'A' },
        F: { '0': 'C', '1': 'G' },
        G: { '0': 'G', '1': 'D' },
        H: { '0': 'A', '1': 'E' },
      },
    },
  },
};
