# Research log — 2026-09-05

This is a human-facing research record. It is deliberately not linked from `SKILL.md` and is not required reading for agents.

## What was inspected

| Source | How checked | What we kept | Why / license result |
|---|---|---|---|
| [arc42/arc42-template](https://github.com/arc42/arc42-template) | Shallow clone; read `LICENSE.txt` and English sections 01, 03–08, 10 | Small adapted Markdown templates for goals, context, strategy, building blocks, runtime, deployment, cross-cutting concepts, and quality requirements | CC BY-SA 4.0. Every adapted template has a credit, license link, and change statement. This keeps the useful document grammar without vendoring arc42. |
| [adr/madr](https://github.com/adr/madr) | Shallow clone; read `LICENSE`, `LICENSE.MIT`, `LICENSE.CC0-1.0`, and `template/adr-template.md` | One lightly adapted ADR template | MIT OR CC0-1.0. Provenance comment is retained. |
| [mermaid-js/mermaid](https://github.com/mermaid-js/mermaid) | Shallow clone; read MIT license and syntax docs for flowchart, sequence, ER | Mermaid as default source-controlled diagram format; five local evidence skeletons and a generation guide | MIT. We did not vendor the engine or docs. The skeletons point to the source and must be filled only with repository evidence. |
| [likec4/likec4](https://github.com/likec4/likec4) | Shallow clone; read MIT license and example `.c4` model/view files | Optional external model/view generator | MIT. Not embedded: it is valuable only when one model needs multiple views. |
| [plantuml-stdlib/C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) | Shallow clone; read MIT license | Optional C4 notation library | Not embedded. Use when the target repo already standardizes on PlantUML/C4. |
| [jgraph/drawio](https://github.com/jgraph/drawio) | Shallow clone; read Apache-2.0 license and searched included diagrams/templates | diagram.net / draw.io as optional editable output format | Apache-2.0. It is an application, not a ready-to-vendor agent skill; no source was copied. |
| [Sunwood-ai-labs/draw-io-skill](https://github.com/Sunwood-ai-labs/draw-io-skill) | Attempted shallow clone | Nothing | Checkout was unusable/broken before files could be inspected, so it was not adopted. Re-evaluate later rather than trusting a summary. |
| [joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record) | Shallow clone; read license | Nothing | The repo's authored material is CC BY-NC-SA; MADR was selected instead because its licensing is clearer for reusable template material. |

## Deliberate choices

- The skill is an orchestrator/reviewer; it does not vendor generator code from any upstream repository.
- Mermaid is the baseline because its source is reviewable in Git and easy to keep close to architecture Markdown.
- `.drawio` is supported only when editability or layout needs justify it. The `.drawio` file remains the source of truth.
- A document or diagram is generated only after repository evidence proves it is useful. Missing source templates are explicitly kept as gaps.
- Repository output default: current-state artifacts go to `docs/architecture/as-is/`; explicitly requested target-state artifacts go to `docs/architecture/to-be/`. This is a local file convention, not an external template or a thinking-layer numbering scheme.

## What to revisit

1. Find a maintained, inspectable draw.io agent skill or an organization-approved diagram.net CLI workflow; then add it as a narrowly scoped optional adapter.
2. Test the skill against two or three real data repos and adjust the artifact selection rules based on observed false positives.
3. If multi-view architecture documentation becomes recurring, trial LikeC4 or Structurizr on one representative repository before adopting either.
