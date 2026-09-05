# Diagram generation

Terms: [terminology.md](terminology.md). This file is about **notation** for **diagram** artifacts that render a **view**. Mermaid and draw.io are not architecture types.

## Mermaid: supported default notation

Use the local `.mmd` skeletons only after choosing a **view** (stakeholder + concern) and deciding a diagram is the right **artifact**. The skeletons are evidence placeholders derived from documented Mermaid syntax, not a universal architecture **template**:

- `../templates/context/system-context.mmd` — Context view (boundary and external exchanges).
- `../templates/static-architecture/data-flow.mmd` — static **building blocks** and **relationships** (stores, pipelines, interfaces).
- `../templates/static-architecture/entity-relationship.mmd` — evidenced logical contract relationships.
- `../templates/runtime/runtime-sequence.mmd` — Runtime view (ingestion, transformation, serving, failure, or recovery **scenario**).
- `../templates/deployment/deployment-topology.mmd` — Deployment view (execution nodes and connections).

Replace every bracketed placeholder; delete unsupported nodes and edges. Keep stable identifiers separate from labels. Mermaid parsing traps confirmed from the source documentation: do not use unquoted lowercase `end` in a flowchart label; quote or bracket it if unavoidable. Use `flowchart LR`, `sequenceDiagram`, and `erDiagram` according to the selected view.

Validate with an existing project Mermaid renderer or `mmdc` when it is already installed. Do not install a renderer or fetch packages merely to validate a small diagram unless the user approves that dependency change. If no renderer is available, perform a syntax review and mark rendering unverified.

## draw.io / diagram.net: conditional notation

The draw.io repository was inspected as an Apache-2.0 application, not adopted as an embedded generator. A public community repo advertised as `Sunwood-ai-labs/draw-io-skill` was also attempted, but its shallow checkout was not usable for inspection; it is not a dependency of this skill.

Use `.drawio` only after Mermaid is insufficient because visual editing, free-form layout, or an organization presentation convention matters. Keep `.drawio` as the canonical **document** for that diagram and save an exported SVG or PNG only when requested. Do not generate raw draw.io XML from memory; use a trusted, available diagram.net generator/editor, or ask for/locate the project's existing draw.io tooling. Record generator/version and any imported assets in the document provenance.

## Escalation rule

If one **architecture model** must yield many interlinked **views**, consider LikeC4 or Structurizr before duplicating diagrams. If the project already has a diagram convention, preserve it unless an explicit change is requested.
