---
name: data-architecture-review
description: Review a data-project repository against architecture thinking layers, identify evidence-backed documentation gaps, and create only the necessary sourced architecture artifacts. Correct mixed terms (building block, view, artifact, pattern, template). Use when the user asks for architecture review, documentation gaps, arc42, data-platform architecture, evidence-led architecture documentation, or when they mix those terms.
---

# Data Architecture Review

Use this skill for an evidence-led architecture review or documentation pass on a data-platform, analytics, ETL/ELT, streaming, lakehouse, or ML-data repository. Do not use it to write a speculative architecture for a repository that has not been inspected.

Thinking layers are the backbone. Terms attach to one slot only. Do not use `artifact`, `document`, `building block`, `view`, `pattern`, or `template` interchangeably. Full slots and the correction table: [terminology.md](references/terminology.md).

## Operating contract

1. Inspect the repository first. Record evidence as paths, configuration keys, code symbols, manifests, tests, or observed runtime/deployment definitions. Label unknowns as unknown; do not infer them as facts.
2. Map evidence to the ten thinking layers in [thinking-layers.md](references/thinking-layers.md). Those layers are **our reasoning order**, not official chapter names of one framework.
3. If the user (or a draft) puts a term in the wrong slot, correct it briefly using [terminology.md](references/terminology.md), then continue with the right term.
4. Decide **viewpoint** (stakeholder + concern) before producing a **view**. Instantiate a [catalog](references/artifact-catalog.md) **template** into an **artifact** (diagram, matrix, catalog, or ADR). Preserve required attribution. State evidence and open questions.
5. Generate the smallest useful set. Prefer Markdown plus Mermaid **documents** committed alongside the repo. Use `.drawio` only when people must edit a complex or presentation-oriented **diagram** visually. Use LikeC4 or Structurizr only when a durable **architecture model** with multiple **views** is justified. Mermaid/PlantUML/LikeC4/draw.io are **notation**, not architecture types.
6. Recheck names, interfaces, stores, topics, jobs, schedules, and deployment claims against repository evidence. Do not present a **diagram** as implementation truth when it includes assumptions. Do not mix abstraction levels in one diagram.

## Output shape

Start with an evidence-to-layer **matrix** (an artifact) and a gap list. For repository file locations, follow [output-conventions.md](references/output-conventions.md). Create only selected **documents**, each holding the chosen artifacts plus provenance, evidence, assumptions, and unresolved questions. A **deliverable** is a package of artifacts for a named audience — do not emit a full suite merely because templates exist.

## Resources

- [terminology.md](references/terminology.md): term slots; correct mixed usage.
- [thinking-layers.md](references/thinking-layers.md): layer meanings and evidence signals.
- [selection-rules.md](references/selection-rules.md): gap triage, diagram format, and consistency checks.
- [artifact-catalog.md](references/artifact-catalog.md): templates, notation, licensing, and when to instantiate.
- [diagram-generation.md](references/diagram-generation.md): read when generating or validating a Mermaid or `.drawio` diagram.
- [output-conventions.md](references/output-conventions.md): read before creating files in a reviewed repository.
