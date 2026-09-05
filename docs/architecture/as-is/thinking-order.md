<!--
Provenance: as-is design walk 2026-09-05. Audience: repository owner learning data-architecture thinking order.
Evidence: prior Motivation/Requirements/Context map plus inspected calendar data and scripts.
This pack is current-state design of *this* platform, not a speculative target architecture.
-->

# Thinking order — conceptual → logical → pattern → physical

Read these artifacts **in this order**. Do not start at Bronze/Silver/Gold or at CSV names.

| Step | Abstraction | Question | Artifact |
|---|---|---|---|
| 0 | Why / what / who | Purpose, constraints, neighbors | [evidence-map.md](evidence-map.md), [diagrams/system-context.mmd](diagrams/system-context.mmd) |
| 1 | Conceptual data model | Which business things exist, and how they relate? | [conceptual-data-model.md](conceptual-data-model.md), [diagrams/conceptual-data.mmd](diagrams/conceptual-data.mmd) |
| 2 | Logical data model | How those things become vendor-neutral data components? | [logical-data-model.md](logical-data-model.md), [diagrams/logical-data.mmd](diagrams/logical-data.mmd) |
| 3 | Architecture pattern | Which processing pattern fits those components? | [solution-strategy.md](solution-strategy.md), [diagrams/medallion-architecture-view.mmd](diagrams/medallion-architecture-view.mmd) |
| 4 | Physical data model | How that pattern is implemented here? | [physical-data-model.md](physical-data-model.md), [diagrams/physical-data-flow.mmd](diagrams/physical-data-flow.mmd) |
| 5 | Traceability | One business concept through every step | [traceability.md](traceability.md) |

**Running example (same business occurrence in every file):** the United States Non-Farm Employment Change print on 4 September 2026, classified high market-impact, with forecast 55K and previous −23K (actual not yet printed in the captured dump).

**Rule:** a sentence that names a table, folder, job, or vendor belongs only in step 4. A sentence that names Bronze/Silver/Gold as *roles* belongs in step 3. Steps 1–2 stay in business and logical language.
