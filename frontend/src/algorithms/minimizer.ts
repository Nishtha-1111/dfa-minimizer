import { DFADefinition, MinimizationStep, MinimizationTrace, AlgorithmType, StateId } from '../types/dfa';

/**
 * Remove states that are unreachable from the start state.
 */
export function removeUnreachableStates(dfa: DFADefinition): {
  prunedDfa: DFADefinition;
  unreachableStates: StateId[];
  steps: MinimizationStep[];
} {
  const reachable = new Set<StateId>();
  const queue: StateId[] = [dfa.start_state];
  reachable.add(dfa.start_state);

  while (queue.length > 0) {
    const current = queue.shift()!;
    for (const sym of dfa.alphabet) {
      const next = dfa.transitions[current]?.[sym];
      if (next && !reachable.has(next)) {
        reachable.add(next);
        queue.push(next);
      }
    }
  }

  const unreachableStates = dfa.states.filter((s) => !reachable.has(s));
  const reachableStates = dfa.states.filter((s) => reachable.has(s));

  const prunedTransitions: Record<StateId, Record<string, StateId>> = {};
  for (const s of reachableStates) {
    prunedTransitions[s] = {};
    for (const sym of dfa.alphabet) {
      prunedTransitions[s][sym] = dfa.transitions[s]?.[sym];
    }
  }

  const prunedDfa: DFADefinition = {
    states: reachableStates,
    alphabet: [...dfa.alphabet],
    start_state: dfa.start_state,
    accept_states: dfa.accept_states.filter((s) => reachable.has(s)),
    transitions: prunedTransitions,
  };

  const steps: MinimizationStep[] = [];
  if (unreachableStates.length > 0) {
    steps.push({
      step_number: 1,
      total_steps: 1,
      phase: 'unreachable_removal',
      title: 'Remove unreachable states',
      explanation: `BFS exploration discovered reachable states: {${reachableStates.join(
        ', '
      )}}. Pruning ${unreachableStates.length} dead/unreachable state(s): {${unreachableStates.join(', ')}}.`,
      formal_notation: `Q_{\\text{pruned}} = Q \\setminus \\{${unreachableStates.join(
        ', '
      )}\\} = \\{${reachableStates.join(', ')}\\}`,
      partition: [reachableStates],
      highlighted_states: unreachableStates,
    });
  }

  return { prunedDfa, unreachableStates, steps };
}

/**
 * Format block for display e.g. ["A", "B"] -> "{A, B}"
 */
export function formatBlock(block: string[]): string {
  return `{${[...block].sort().join(', ')}}`;
}

/**
 * Run Hopcroft's partition refinement algorithm.
 */
export function runHopcroft(dfaInput: DFADefinition): MinimizationTrace {
  const { prunedDfa, unreachableStates, steps: unreachableSteps } = removeUnreachableStates(dfaInput);

  const states = [...prunedDfa.states].sort();
  const alphabet = [...prunedDfa.alphabet].sort();
  const acceptSet = new Set(prunedDfa.accept_states);

  const F = states.filter((s) => acceptSet.has(s));
  const nonF = states.filter((s) => !acceptSet.has(s));

  // Initial partition P
  let P: string[][] = [];
  if (F.length > 0 && nonF.length > 0) {
    // Sort so non-accepting comes first or accepting comes first consistently
    P = [nonF.sort(), F.sort()];
  } else if (F.length > 0) {
    P = [F.sort()];
  } else {
    P = [nonF.sort()];
  }

  // Worklist W: set of blocks
  // By standard textbook Hopcroft, we enqueue the smaller block or both
  const W: string[][] = [];
  if (F.length > 0 && nonF.length > 0) {
    if (F.length <= nonF.length) {
      W.push([...F]);
    } else {
      W.push([...nonF]);
    }
  } else if (P.length > 0) {
    W.push([...P[0]]);
  }

  const rawSteps: Omit<MinimizationStep, 'step_number' | 'total_steps'>[] = [];

  // Initial Step
  rawSteps.push({
    phase: 'initial_partition',
    title: 'Initial partition into accepting and non-accepting states',
    explanation:
      F.length > 0 && nonF.length > 0
        ? `We partition the states into accepting states ${formatBlock(
            F
          )} and non-accepting states ${formatBlock(
            nonF
          )}. States in different groups can never be equivalent because one accepts and the other rejects.`
        : `All states belong to the same category (${F.length > 0 ? 'accepting' : 'non-accepting'}).`,
    formal_notation: `P_0 = \\{F, Q \\setminus F\\} = \\{${formatBlock(F)}, ${formatBlock(nonF)}\\}`,
    partition: P.map((b) => [...b]),
    highlighted_states: [...F],
  });

  // Precompute reverse transitions: inv[sym][target] = set of states that transition to target on sym
  const inv: Record<string, Record<string, string[]>> = {};
  for (const sym of alphabet) {
    inv[sym] = {};
    for (const s of states) {
      const target = prunedDfa.transitions[s]?.[sym];
      if (target) {
        if (!inv[sym][target]) inv[sym][target] = [];
        inv[sym][target].push(s);
      }
    }
  }

  // Worklist iteration
  while (W.length > 0) {
    const A = W.shift()!;
    const A_sorted = [...A].sort();

    for (const c of alphabet) {
      // Find X = predecessor states that lead into A on symbol c
      const X_set = new Set<string>();
      for (const target of A) {
        const predecessors = inv[c]?.[target] || [];
        for (const p of predecessors) {
          X_set.add(p);
        }
      }

      const X = Array.from(X_set).sort();
      let anySplitInThisCheck = false;
      const nextP: string[][] = [];

      for (const Y of P) {
        const Y1: string[] = []; // Y ∩ X
        const Y2: string[] = []; // Y \ X

        for (const state of Y) {
          if (X_set.has(state)) {
            Y1.push(state);
          } else {
            Y2.push(state);
          }
        }

        if (Y1.length > 0 && Y2.length > 0) {
          // Split occurred!
          anySplitInThisCheck = true;
          Y1.sort();
          Y2.sort();
          nextP.push(Y1);
          nextP.push(Y2);

          // Update worklist W
          const wIndex = W.findIndex(
            (b) => b.length === Y.length && [...b].sort().join(',') === [...Y].sort().join(',')
          );
          if (wIndex !== -1) {
            W.splice(wIndex, 1);
            W.push(Y1);
            W.push(Y2);
          } else {
            if (Y1.length <= Y2.length) {
              W.push(Y1);
            } else {
              W.push(Y2);
            }
          }

          rawSteps.push({
            phase: 'refinement',
            title: `Split group ${formatBlock(Y)} on symbol '${c}'`,
            explanation: `Inspecting states transitioning into ${formatBlock(
              A_sorted
            )} on symbol '${c}'. States {${Y1.join(', ')}} transition into ${formatBlock(
              A_sorted
            )}, while states {${Y2.join(', ')}} do not. Thus, ${formatBlock(
              Y
            )} splits into ${formatBlock(Y1)} and ${formatBlock(Y2)}.`,
            formal_notation: `X = \\delta^{-1}(${formatBlock(A_sorted)}, '${c}') = \\{${X.join(
              ', '
            )}\\}\n${formatBlock(Y)} \\cap X = ${formatBlock(Y1)}, \\quad ${formatBlock(
              Y
            )} \\setminus X = ${formatBlock(Y2)}`,
            partition: [...nextP, ...P.filter((other) => other !== Y)].map((b) => [...b]),
            active_splitter: {
              block: A_sorted,
              symbol: c,
            },
            highlighted_states: [...Y1, ...Y2],
            split_happened: true,
          });
        } else {
          nextP.push(Y);
        }
      }

      if (!anySplitInThisCheck) {
        // Detailed pedagogical step when no split occurs
        const relevantStatesInX = X.filter((s) => states.includes(s));
        const explanationText =
          relevantStatesInX.length > 0
            ? `Look at every state that moves into ${formatBlock(
                A_sorted
              )} on input ${c}. ${relevantStatesInX.join(
                ' and '
              )} both do, and they sit in the same group, so no group needs to be split.`
            : `No states transition into splitter ${formatBlock(
                A_sorted
              )} on symbol '${c}', so no groups need to be split.`;

        rawSteps.push({
          phase: 'refinement',
          title: `Split using the group ${formatBlock(A_sorted)}`,
          explanation: explanationText,
          formal_notation: `A = ${formatBlock(A_sorted)}, \\, c = '${c}'\n\\delta^{-1}(A, '${c}') = \\{${X.join(
            ', '
          )}\\}\n\\forall Y \\in P, \\; Y \\subseteq X \\lor Y \\cap X = \\emptyset`,
          partition: P.map((b) => [...b]),
          active_splitter: {
            block: A_sorted,
            symbol: c,
          },
          highlighted_states: relevantStatesInX,
          split_happened: false,
        });
      }

      P = nextP;
    }
  }

  // Construct final minimized DFA
  const finalSteps = unreachableSteps.concat(
    rawSteps.map((s, idx) => ({
      ...s,
      step_number: unreachableSteps.length + idx + 1,
      total_steps: 0, // will patch below
    }))
  );

  const blockMap: Record<StateId, string> = {};
  P.forEach((block) => {
    const blockLabel = formatBlock(block);
    block.forEach((state) => {
      blockMap[state] = blockLabel;
    });
  });

  const minStates = P.map((b) => formatBlock(b));
  const minStartState = blockMap[prunedDfa.start_state];
  const minAcceptStates = Array.from(
    new Set(prunedDfa.accept_states.map((s) => blockMap[s]).filter(Boolean))
  );

  const minTransitions: Record<string, Record<string, string>> = {};
  for (const block of P) {
    const rep = block[0];
    const bLabel = formatBlock(block);
    minTransitions[bLabel] = {};
    for (const sym of alphabet) {
      const dest = prunedDfa.transitions[rep]?.[sym];
      if (dest) {
        minTransitions[bLabel][sym] = blockMap[dest];
      }
    }
  }

  const finalDfa: DFADefinition = {
    states: minStates,
    alphabet: [...alphabet],
    start_state: minStartState,
    accept_states: minAcceptStates,
    transitions: minTransitions,
  };

  finalSteps.push({
    step_number: finalSteps.length + 1,
    total_steps: 0,
    phase: 'final',
    title: 'Minimization Complete',
    explanation: `The partition is stable with ${P.length} state-groups. Each group collapses into a single state in the minimal DFA.`,
    formal_notation: `P_{\\text{final}} = \\{${P.map((b) => formatBlock(b)).join(
      ', '
    )}\\}\n|Q_{\\min}| = ${P.length}`,
    partition: P.map((b) => [...b]),
    minimized_dfa: finalDfa,
  });

  const total = finalSteps.length;
  finalSteps.forEach((s) => {
    s.total_steps = total;
  });

  return {
    algorithm: 'hopcroft',
    original_dfa: dfaInput,
    unreachable_removed: unreachableStates,
    pruned_dfa: prunedDfa,
    steps: finalSteps,
    final_dfa: finalDfa,
    state_mapping: blockMap,
  };
}

/**
 * Run Moore's algorithm (k-equivalence).
 */
export function runMoore(dfaInput: DFADefinition): MinimizationTrace {
  const { prunedDfa, unreachableStates, steps: unreachableSteps } = removeUnreachableStates(dfaInput);

  const states = [...prunedDfa.states].sort();
  const alphabet = [...prunedDfa.alphabet].sort();
  const acceptSet = new Set(prunedDfa.accept_states);

  const F = states.filter((s) => acceptSet.has(s));
  const nonF = states.filter((s) => !acceptSet.has(s));

  let P: string[][] = [];
  if (F.length > 0 && nonF.length > 0) {
    P = [nonF.sort(), F.sort()];
  } else if (F.length > 0) {
    P = [F.sort()];
  } else {
    P = [nonF.sort()];
  }

  const rawSteps: Omit<MinimizationStep, 'step_number' | 'total_steps'>[] = [];

  rawSteps.push({
    phase: 'initial_partition',
    title: '0-Equivalence: Separate accept and non-accept states',
    explanation: `States are initially partitioned into accepting ${formatBlock(
      F
    )} and non-accepting ${formatBlock(
      nonF
    )}. This establishes the 0-equivalence relation (distinguishing by the empty string ε).`,
    formal_notation: `\\Pi_0 = \\{F, Q \\setminus F\\} = \\{${formatBlock(F)}, ${formatBlock(
      nonF
    )}\\}`,
    partition: P.map((b) => [...b]),
    highlighted_states: [...F],
  });

  let k = 1;
  let changed = true;

  while (changed) {
    changed = false;
    const blockIndexMap: Record<string, number> = {};
    P.forEach((block, idx) => {
      block.forEach((s) => {
        blockIndexMap[s] = idx;
      });
    });

    const nextP: string[][] = [];

    for (const group of P) {
      if (group.length <= 1) {
        nextP.push(group);
        continue;
      }

      // Group states by signature (vector of target block indices on each symbol)
      const sigMap = new Map<string, string[]>();
      for (const state of group) {
        const sig = alphabet
          .map((sym) => {
            const next = prunedDfa.transitions[state]?.[sym];
            return next !== undefined ? blockIndexMap[next] : -1;
          })
          .join('|');

        if (!sigMap.has(sig)) {
          sigMap.set(sig, []);
        }
        sigMap.get(sig)!.push(state);
      }

      const subBlocks = Array.from(sigMap.values()).map((b) => b.sort());
      if (subBlocks.length > 1) {
        changed = true;
        subBlocks.forEach((sb) => nextP.push(sb));

        rawSteps.push({
          phase: 'refinement',
          title: `Round ${k}: Partition block ${formatBlock(group)} splits`,
          explanation: `States in ${formatBlock(
            group
          )} transition into different blocks on input symbols. It splits into ${subBlocks
            .map((b) => formatBlock(b))
            .join(' and ')}.`,
          formal_notation: `\\Pi_{${k}} \\text{ separates } ${formatBlock(
            group
          )} \\rightarrow ${subBlocks.map((b) => formatBlock(b)).join(', ')}`,
          partition: [...nextP, ...P.filter((other) => other !== group)].map((b) => [...b]),
          highlighted_states: group,
          split_happened: true,
        });
      } else {
        nextP.push(group);
      }
    }

    if (!changed) {
      rawSteps.push({
        phase: 'refinement',
        title: `Round ${k}: Partition is stable`,
        explanation: `No states within any block transition to different blocks. \\Pi_{${k}} = \\Pi_{${
          k - 1
        }}, terminating Moore's algorithm.`,
        formal_notation: `\\Pi_{${k}} = \\Pi_{${k - 1}}`,
        partition: P.map((b) => [...b]),
        split_happened: false,
      });
    }

    P = nextP;
    k++;
  }

  // Construct final minimized DFA
  const finalSteps = unreachableSteps.concat(
    rawSteps.map((s, idx) => ({
      ...s,
      step_number: unreachableSteps.length + idx + 1,
      total_steps: 0,
    }))
  );

  const blockMap: Record<StateId, string> = {};
  P.forEach((block) => {
    const blockLabel = formatBlock(block);
    block.forEach((state) => {
      blockMap[state] = blockLabel;
    });
  });

  const minStates = P.map((b) => formatBlock(b));
  const minStartState = blockMap[prunedDfa.start_state];
  const minAcceptStates = Array.from(
    new Set(prunedDfa.accept_states.map((s) => blockMap[s]).filter(Boolean))
  );

  const minTransitions: Record<string, Record<string, string>> = {};
  for (const block of P) {
    const rep = block[0];
    const bLabel = formatBlock(block);
    minTransitions[bLabel] = {};
    for (const sym of alphabet) {
      const dest = prunedDfa.transitions[rep]?.[sym];
      if (dest) {
        minTransitions[bLabel][sym] = blockMap[dest];
      }
    }
  }

  const finalDfa: DFADefinition = {
    states: minStates,
    alphabet: [...alphabet],
    start_state: minStartState,
    accept_states: minAcceptStates,
    transitions: minTransitions,
  };

  finalSteps.push({
    step_number: finalSteps.length + 1,
    total_steps: 0,
    phase: 'final',
    title: 'Minimization Complete',
    explanation: `Stable equivalence classes found. Resulting DFA has ${P.length} states.`,
    formal_notation: `\\Pi_{\\text{final}} = \\{${P.map((b) => formatBlock(b)).join(
      ', '
    )}\\}\n|Q_{\\min}| = ${P.length}`,
    partition: P.map((b) => [...b]),
    minimized_dfa: finalDfa,
  });

  const total = finalSteps.length;
  finalSteps.forEach((s) => {
    s.total_steps = total;
  });

  return {
    algorithm: 'moore',
    original_dfa: dfaInput,
    unreachable_removed: unreachableStates,
    pruned_dfa: prunedDfa,
    steps: finalSteps,
    final_dfa: finalDfa,
    state_mapping: blockMap,
  };
}
