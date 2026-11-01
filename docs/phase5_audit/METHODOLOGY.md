# Phase 5 — Methodology

## CHSH geometry

- A0 = 0 degrees
- A1 = 90 degrees
- B0 = 45 degrees
- B1 = -45 degrees

Quantum singlet CHSH magnitude:

\[
S=2\sqrt{2}
\]

## Deterministic local hidden-variable model

The hidden-variable space consists of 16 deterministic
strategies:

\[
\lambda=(A_0,A_1,B_0,B_1)\in\{-1,+1\}^{4}
\]

A conditional distribution over these strategies is specified
for each of the four setting pairs.

## Total variation

\[
TV(P,Q)=\frac12\sum_\lambda |P(\lambda)-Q(\lambda)|
\]

Declared Hall metric convention:

\[
M_{\mathrm{Hall}}=2TV
\]

Hall inequality used:

\[
S\leq2+3M_{\mathrm{Hall}}
\]

Therefore:

\[
TV\geq\frac{S-2}{6}
=\frac{\sqrt2-1}{3}
\]

The theorem assumptions and metric conversion must be
interpreted relative to the declared model.

## Exact algebraic verification

Exact candidate probabilities:

\[
p_{\mathrm{small}}=\frac{2-\sqrt2}{8}
\]

\[
p_{\mathrm{large}}=\frac{2+\sqrt2}{24}
\]

Arithmetic was performed in \(\mathbb{Q}(\sqrt2)\).

Six checks passed:

1. Exact nonnegative probabilities.
2. Four exact normalisations.
3. All 16 target probability equations.
4. All six pairwise TV values.
5. Exact Hall lower-bound evaluation.
6. Primal attainment of the analytical lower bound.

## Historical recovery

The examined refs, commits, source blobs, candidate Phase 5
paths, notebook cells and unreachable Git objects did not yield
the original LP implementation or its exact historical
constraint ordering.

This is a bounded recovery conclusion.
