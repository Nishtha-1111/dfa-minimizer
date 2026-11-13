export type StateId = string;
export type SymbolChar = string;

export interface DFADefinition {
  states: StateId[];
  alphabet: SymbolChar[];
  start_state: StateId;
  accept_states: StateId[];
  transitions: Record<StateId, Record<SymbolChar, StateId>>;
}

export type AlgorithmType = 'table_filling' | 'moore';

export interface TraceStepHighlights {
  active_states: string[];
  splitter_block: string[];
  unreachable_states: string[];
  split_blocks: string[][];
  marked_pairs?: string[][];
  active_pair?: string[];
  target_pair?: string[];
  mark_reason?: string;
}

export interface TraceStep {
  step_id: number;
  total_steps: number;
  phase: 'unreachable_removal' | 'initial_partition' | 'refinement' | 'done';
  title: string;
  description: string;
  notation?: string;
  highlights: TraceStepHighlights;
  partition_state: string[][];
}

export interface MinimizeResponse {
  algorithm: string;
  original_dfa: DFADefinition;
  unreachable_states: string[];
  pruned_dfa: DFADefinition;
  trace: TraceStep[];
  minimal_dfa: DFADefinition;
  state_mapping: Record<string, string>;
  is_already_minimal: boolean;
}

export interface ValidationResponse {
  is_valid: boolean;
  is_complete: boolean;
  errors: string[];
  warnings: string[];
  missing_transitions: { state: string; symbol: string }[];
  dead_state_candidate?: string;
}

export interface ExecutionResult {
  accepted: boolean;
  path: string[];
  error?: string | null;
}

export interface SimulateResponse {
  input_string: string;
  is_valid_alphabet: boolean;
  alphabet_error?: string | null;
  original_result: ExecutionResult;
  minimized_result?: ExecutionResult | null;
  agreement: boolean;
}
