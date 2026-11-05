# Automata Theory & Minimization Algorithms

This document provides a rigorous mathematical and algorithmic explanation of all theoretical foundations used in the DFA Minimizer.

---

## 1. Formal Definition of a DFA

A Deterministic Finite Automaton (DFA) is formally defined as a 5-tuple:
$$M = (Q, \Sigma, \delta, q_0, F)$$
Where:
- $Q$: Finite, non-empty set of states.
- $\Sigma$: Finite alphabet of input symbols.
- $\delta: Q \times \Sigma \to Q$: The total transition function.
- $q_0 \in Q$: The unique initial (start) state.
- $F \subseteq Q$: The set of accepting (final) states.

The extended transition function $\delta^*: Q \times \Sigma^* \to Q$ describes the destination state after reading a full input string $w = a_1 a_2 \dots a_k$:
$$\delta^*(q, \varepsilon) = q$$
$$\delta^*(q, wa) = \delta(\delta^*(q, w), a)$$

A string $w \in \Sigma^*$ is accepted by $M$ if and only if $\delta^*(q_0, w) \in F$.

---

## 2. Preprocessing: Elimination of Unreachable States

Before executing any minimization algorithm, all unreachable states must be detected and removed. If unreachable states are retained, they could distort the equivalence classes of the reachable quotient machine.

### Reachability Definition
A state $q \in Q$ is reachable if there exists a string $w \in \Sigma^*$ such that:
$$\delta^*(q_0, w) = q$$

### BFS Reachability Algorithm
1. **Initialize**: Set $\text{Visited} = \{ q_0 \}$ and a queue $\mathcal{Q} = [q_0]$.
2. **Exploration**:
   - While $\mathcal{Q}$ is not empty:
     - Dequeue state $u$.
     - For each symbol $a \in \Sigma$:
       - Let $v = \delta(u, a)$.
       - If $v \notin \text{Visited}$:
         - Add $v$ to $\text{Visited}$.
         - Enqueue $v$ into $\mathcal{Q}$.
3. **Pruning**:
   - The pruned set of states is $Q' = \text{Visited}$.
   - Prune transitions: $\delta' = \delta \vert_{Q' \times \Sigma \to Q'}$.
   - Prune final states: $F' = F \cap Q'$.
   - Unreachable states are $Q \setminus Q'$.

---

## 3. Algorithm 1: The Table-Filling Method (Myhill-Nerode)

### Theoretical Foundation: State Equivalence
Two states $p, q \in Q$ are defined as **equivalent** ($p \sim q$) if no string in $\Sigma^*$ can distinguish between them:
$$p \sim q \iff \forall w \in \Sigma^*, \; (\delta^*(p, w) \in F \iff \delta^*(q, w) \in F)$$

If there exists even one string $w \in \Sigma^*$ such that:
$$\delta^*(p, w) \in F \land \delta^*(q, w) \notin F \quad (\text{or vice versa})$$
then $p$ and $q$ are **distinguishable** ($p \not\sim q$). The string $w$ is called a **distinguishing witness**.

### Structure of the Distinguishability Table
Because equivalence is symmetric ($p \sim q \iff q \sim p$) and reflexive ($p \sim p$ is trivial), we only need to inspect pairs $\{p, q\}$ where $p < q$ in a fixed total ordering of $Q$.
- Total unordered pairs:
  $$\binom{|Q|}{2} = \frac{|Q|(|Q| - 1)}{2}$$
- This forms a **lower-triangular matrix**:
  - Rows: $q_1, q_2, \dots, q_{n-1}$
  - Columns: $q_0, q_1, \dots, q_{n-2}$

### Algorithm Steps

```
┌────────────────────────────────────────────────────────────────────────┐
│                      TABLE-FILLING ALGORITHM                           │
│                                                                        │
│  Step 1 (Base Case - 0-distinguishability):                            │
│    For each pair {p, q}:                                               │
│      If (p ∈ F and q ∉ F) or (p ∉ F and q ∈ F):                        │
│        Mark {p, q} with ✕  [Distinguished by ε]                        │
│                                                                        │
│  Step 2 (Inductive Step - Fixed-Point Iteration):                      │
│    Repeat until no new marks occur in a full pass:                     │
│      For each UNMARKED pair {p, q}:                                    │
│        For each symbol a ∈ Σ:                                          │
│          p' = δ(p, a),  q' = δ(q, a)                                   │
│          If p' ≠ q' and {p', q'} is ALREADY MARKED:                    │
│            Mark {p, q} with ✕                                          │
│            Witness symbol: a; Witness pair: {p', q'}                   │
│                                                                        │
│  Step 3 (Quotient DFA Construction):                                   │
│    All unmarked cells {p, q} are EQUIVALENT (p ~ q).                   │
│    Use Disjoint Set Union (DSU) to merge equivalent states into        │
│    compound quotient states: [q] = { s ∈ Q | s ~ q }.                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Algorithm 2: Moore's Partition Refinement Algorithm

Moore’s algorithm minimizes DFAs through iterative partition refinement using the concept of **$k$-equivalence**.

### $k$-Equivalence Definition
- **0-equivalence** ($p \sim_0 q$):
  $$p \sim_0 q \iff (p \in F \iff q \in F)$$
- **$k$-equivalence** ($p \sim_k q$ for $k \ge 1$):
  $$p \sim_k q \iff (p \sim_{k-1} q) \;\land\; \forall a \in \Sigma, \; \delta(p, a) \sim_{k-1} \delta(q, a)$$

States are truly equivalent ($p \sim q$) if and only if they are $k$-equivalent for all $k \ge 0$. Since $Q$ is finite, the sequence of partitions $P_0, P_1, P_2, \dots$ must stabilize in at most $|Q| - 2$ iterations.

### Partition Refinement Steps

1. **Initial Partition ($P_0$)**:
   $$P_0 = \{ F,\; Q \setminus F \}$$
2. **Refinement Iterations ($P_k \to P_{k+1}$)**:
   - For each block $B \in P_k$:
     - Compute the **transition signature** for each state $s \in B$:
       $$\text{Signature}(s) = \Big( \text{BlockID}_{P_k}(\delta(s, a_1)),\; \text{BlockID}_{P_k}(\delta(s, a_2)),\; \dots \Big)$$
     - Group states within $B$ that have identical signatures.
     - If all states in $B$ have the same signature, $B$ remains intact in $P_{k+1}$.
     - If states have differing signatures, $B$ splits into sub-blocks corresponding to each distinct signature.
3. **Termination Condition**:
   - The algorithm terminates when $P_{k+1} = P_k$ (no blocks split).
   - Each block in the final partition represents a single consolidated state in the minimal DFA.

---

## 5. Dual-DFA String Simulation & Verification Engine

To prove that the minimal DFA $M'$ accepts the exact same formal language as the original DFA $M$ ($L(M') = L(M)$):

1. Given an input string $w = c_1 c_2 \dots c_m \in \Sigma^*$.
2. Compute state path on original machine $M$:
   $$q_0 \xrightarrow{c_1} q_1 \xrightarrow{c_2} q_2 \dots \xrightarrow{c_m} q_m$$
   Result is **Accepted** if $q_m \in F$, otherwise **Rejected**.
3. Compute state path on minimal quotient machine $M'$:
   $$[q_0] \xrightarrow{c_1} [q_1] \xrightarrow{c_2} [q_2] \dots \xrightarrow{c_m} [q_m]$$
   Result is **Accepted** if $[q_m] \in F'$, otherwise **Rejected**.
4. Both results are compared side by side, confirming behavioral equivalence across every character step.
