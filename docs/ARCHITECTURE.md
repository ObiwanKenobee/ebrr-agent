# EBRR architecture

## Design principle

**Ground before generating; verify before declaring success.** The agent maintains an inspectable chain from issue description to retrieved repository evidence, diagnosis, proposed patch, and verification outcome.

## Proposed flow

```text
Issue description
      |
      v
Issue interpreter -----> structured task and expected behavior
      |
      v
Symbol grounder -------> candidate paths / symbols / tests
      |
      v
Repository navigator --> graph and embedding retrieval
      |
      v
Evidence ledger -------> provenance + epistemic state
      |
      v
Decision controller ---> next inspection / stop / test / patch
      |
      v
Patch generator -------> minimal candidate modification
      |
      v
Patch verifier --------> targeted tests + regression checks
      |
      v
Run record ------------> outcome, budget usage, failure analysis
```

## Components

### 1. Issue interpreter

Extract the observed behavior, expected behavior, constraints, environment, and key terms from the task description. Preserve uncertainty and do not treat issue prose as proof of root cause.

### 2. Symbol grounder

Map issue language to candidate files, functions, classes, methods, tests, and error locations. Candidate ranking should be measured independently from final repair success.

### 3. Repository navigator

Use the available repository index, AST/code graph, symbol metadata, and embeddings. The adapter must document the actual harness interface; never assume that a retrieval endpoint accepts arbitrary natural-language text unless verified.

### 4. Evidence ledger

Record each evidence item with a stable identifier, source locator, kind, epistemic status, and the claim it supports or challenges. Avoid copying source code unnecessarily. Distinguish direct observations from hypotheses and interpretations.

### 5. Decision controller

Select the next action based on expected information value and remaining budget. Candidate actions may include opening a file, expanding a graph neighborhood, inspecting a test, running a test, or stopping. The first implementation may use a simple deterministic policy; learned policies are a later experiment.

### 6. Patch generator

Generate a minimal candidate patch only after sufficient evidence is available. The patch rationale should cite evidence identifiers, not merely restate the issue.

### 7. Patch verifier

Run available targeted tests and regression checks. Report exactly what ran, what passed, what failed, and what could not be run. A generated patch is not a successful repair until the benchmark's specified verifier accepts it.

## Resource budget

A run records at least:

- Prompt and completion tokens, when exposed by the runtime.
- Tool calls.
- Graph expansions or traversed edges/nodes, depending on harness telemetry.
- Verification actions and execution time.
- Wall-clock duration and hardware/runtime details.

Do not combine these into one opaque efficiency score without also publishing the underlying measurements.

## Evidence model

The initial Python abstractions are intentionally generic. Benchmark-specific concepts belong in adapters. The evidence ledger should support:

- `OBSERVED`: directly retrieved or executed evidence.
- `HYPOTHESIS`: a proposed explanation not yet established.
- `CONTRADICTED`: evidence that weakens or rules against a claim.

Evidence kind and epistemic status are separate dimensions. For example, a test failure is an execution observation; the claim that a particular function caused it may still be a hypothesis.
