# Repository output conventions

Terms: [terminology.md](terminology.md). Paths below are **documents** (files). What we write *into* them are **artifacts** (matrix, diagram, catalog, ADR). A named handover pack is a **deliverable**.

Use these defaults only when the repository has no established architecture-documentation location or naming convention. Existing maintained conventions win.

## Current-state documents

Current-state writing is evidence-backed observation, not a proposal. Put files under:

```text
docs/architecture/as-is/
├── evidence-map.md
├── foundation.md              # optional
└── diagrams/
    └── system-context.mmd     # optional
```

- `evidence-map.md` is the first durable **document** when the user asks to persist a review. The **artifact** inside is an evidence **matrix** across thinking layers (facts, assumptions, unknowns, open questions).
- `foundation.md` is optional prose that combines only the selected Motivation, Requirements, and Context content. It is a compact **document**, not a replacement for the ARC-01 / ARC-03 **templates**.
- `diagrams/*.mmd` are documents holding **diagram** artifacts for a chosen **view**. Use Mermaid by default; only place `.drawio` here when visual editing is materially necessary.

Do not create any of these files for a review-only request unless the user asks for persistent documentation.

## Target-state documents

Create this directory only for an explicitly requested future/target architecture:

```text
docs/architecture/to-be/
```

Keep it separate from `as-is`. Each target-state **artifact** must identify which current-state evidence, assumptions, decisions, and unresolved gaps it depends on.

## Naming and growth

Use descriptive names rather than numeric “levels.” When a compact document becomes hard to review, split by layer or audience while retaining the `as-is` or `to-be` boundary. Do not manufacture empty folders or documents merely to mirror all ten thinking layers.
