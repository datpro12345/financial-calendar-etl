# Terminology

This skill's **thinking layers** are the backbone. They are our reasoning order, not official chapter names of one framework.

Do not use `artifact`, `document`, `building block`, `view`, `pattern`, or `template` as if they meant the same thing. Read this file whenever the user (or a draft) mixes those words.

## Correction protocol

When the user uses a term in the wrong slot, correct it in one or two sentences, then continue with the right term. Do not lecture. Do not rename their files unless they ask.

| If they say… | Usually they mean… | Say instead |
|---|---|---|
| “tạo building block Medallion / C4 / Mermaid” | pattern, viewpoint, or notation | Medallion is a **pattern**; C4 container is an **element**; Mermaid is **notation** |
| “view Bronze/Silver/Gold” | stores produced by applying a pattern | Bronze/Silver/Gold **stores** are **building blocks**; a Data Flow **View** may *show* them |
| “artifact architecture” when pointing at the system | the model | **Architecture model** (elements + relationships) |
| “document” as the architecture type | the file that holds content | **Document** = file; it may contain several **artifacts** |
| “deliverable” for one `.mmd` | one diagram | that file is a **document** containing a **diagram artifact** |
| “template” for this project's architecture | instantiated output | **Template** + evidence → **artifact** |
| mixing Customer, Container, and `SELECT` in one picture | mixed abstraction | split **views**; do not mix element types in one **diagram** |

## Thinking flow (ours)

```text
1. MOTIVATION
   Why are we doing this?
        ↓
2. REQUIREMENTS
   What must be true?
        ↓
3. CONTEXT
   What is in/out of scope?
        ↓
4. STATIC ARCHITECTURE
   What things exist?
        ↓
5. RUNTIME / BEHAVIOR
   How do those things interact?
        ↓
6. SOLUTION STRATEGY
   What architectural approach/pattern do we choose?
        ↓
7. DEPLOYMENT
   Where/how does it physically run?
        ↓
8. CROSS-CUTTING CONCERNS
   What rules apply across everything?
        ↓
9. DECISIONS
   Why did we choose this instead of alternatives?
        ↓
10. DELIVERABLE
    What package do we give stakeholders?
```

## Term slots

### Building block / element

A **thing** in the architecture. Use only when answering “architecture comprises what?”

Examples: Customer Data, Ingestion Service, Transformation Engine, Gold Data Store, Metadata Service, Power BI Semantic Model.

C4 names for elements (not diagrams): Person, Software System, Container, Component, Code.

arc42 Building Block View describes static decomposition of these things.

### Relationship

How two building blocks connect. Directed and labelled.

Example: Source ── sends transactions to ──> Ingestion Service.

### Architecture model

The structured set of **elements + relationships**. One model can feed many views.

Pattern **guides** the model. A reference architecture **suggests a starting structure** for the model.

### Viewpoint

Rules for producing a view: which stakeholder, which concern, which element types, which notation, which relationships.

This skill's templates are close to **viewpoints** (how to examine a concern), not the project's architecture.

### View

A selection from the model for one concern. **A view is not a building block.**

Same model, different views (Security View vs Data Flow View).

Rule: if the question is “from which angle do I look?” → **View**.

### Diagram

One rendering of a view. C4 diagram *types* are artifacts that depict views (System Context Diagram, Container Diagram, …).

Mermaid, PlantUML, LikeC4, Structurizr, draw.io are **notation / rendering**, not architecture types.

```text
Architecture Model → Container View → Container Diagram
```

### Artifact

A tangible architecture-work output. Broader than diagram.

```text
Artifact
├── Diagram
├── Matrix
├── Catalog
└── Decision Record
```

Every diagram can be an artifact; not every artifact is a diagram.

### Document

A file that holds content (`architecture.md`, a PDF). Generic. Do not use it to classify architecture semantics. One document may contain several artifacts plus prose.

### Deliverable

The package handed to stakeholders. Usually contains multiple artifacts.

```text
Deliverable
├── Artifact A
├── Artifact B
└── explanatory text
```

### Pattern

A reusable architectural approach (Medallion, Data Mesh, Lambda, event-driven). Not a building block, view, or artifact.

```text
Medallion Pattern  → applied to the model →  Bronze Store, Silver Store, Gold Store (building blocks)
```

### Reference architecture

A published sample structure (sources → ingestion → storage → processing → serving). Instantiate it; do not copy it as this project's model.

### Template

A blank used to create an artifact. Not this project's architecture.

```text
Template + project evidence → Artifact
```

## Map to thinking layers

| Thinking layer | You are reasoning about | Terms to use |
|---|---|---|
| Motivation | why | Driver, Goal, Principle, Stakeholder |
| Requirements | what must hold | Requirement, Constraint, Quality Attribute |
| Context | boundary and outside world | Context **model** / Context **view** |
| Static Architecture | what exists | **Building blocks / elements + relationships** |
| Runtime | how they interact | Runtime **model** / **view**, Scenario |
| Solution Strategy | overall approach | **Pattern**, Strategy, Reference architecture |
| Deployment | logical → physical mapping | Deployment **model** / **view** |
| Cross-cutting | rules across blocks | Concern, Policy, Concept |
| Decisions | why A not B | Architecture Decision / ADR (**artifact**) |
| Communication (not a numbered layer) | how a stakeholder looks | **View / Viewpoint** |
| Output (not a numbered layer) | what is stored as work product | **Artifact** |
| Packaging | what is handed over | **Deliverable** (layer 10) |

## C4 in these slots

| Phrase | Slot |
|---|---|
| Container | element / building block |
| Container View | view (concern: static decomposition at container level) |
| Container Diagram | artifact (diagram) |
| Mermaid | notation |
| `architecture-container.mmd` | document (file) containing that diagram |

Do not call all four “building blocks”.

## Sentence to keep

> Architecture comprises Building Blocks and Relationships.  
> Model organises them.  
> View selects the part to examine.  
> Diagram / Matrix / Catalog are Artifacts that represent them.  
> Document contains artifacts.  
> Deliverable packages them for handover.  
> Pattern guides how to design.  
> Template guides how to create an artifact.

Do not mix abstraction levels in one diagram.
