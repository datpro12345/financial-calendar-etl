# LLM Analyst Playbook

## 0. Mục tiêu

Xây một cách làm để LLM hỗ trợ analyst:

- không chỉ viết report từ KPI có sẵn;
- không chỉ chạy checklist/rubric;
- vẫn có khả năng khám phá insight chưa được con người đặt câu hỏi trước;
- mọi claim quan trọng phải trace được về evidence;
- analysis có cơ chế review/challenge trước khi trở thành kết luận.

Playbook này không giả định LLM là autonomous senior analyst.

Nó coi LLM là một **reasoning + exploration layer** đứng trên deterministic tools như SQL, Python, BI engine và dữ liệu gốc.

---

# 1. Nguồn gốc tư duy

## Principle A — Fuzzy judgment nên được làm explicit

### Source: Andrej Karpathy — `jobs`

Trong project `karpathy/jobs`, các occupation không được đưa cho LLM với yêu cầu chung kiểu “hãy đánh giá AI impact”.

Karpathy định nghĩa:

- một scoring axis rõ ràng;
- thang điểm 0–10;
- scoring methodology;
- heuristic/anchors;
- source data của từng occupation;
- rationale cho mỗi score.

Pipeline thậm chí có bước riêng:

`source → parse → tabulate → LLM score using rubric → persist scores`. citeturn628493search1turn628493search3


### Bài học

Khi business judgment lặp đi lặp lại, không nên để prompt hoàn toàn mở.

Hãy biến những thứ đã biết quan trọng thành:

- criteria;
- scoring rules;
- definitions;
- anchors;
- required checks.

### Trong analyst

Đây trở thành:

**Known Analysis Rubric / Scorecard**

Ví dụ:

- Revenue
- Margin
- Conversion
- SLA
- Forecast variance
- Known business risks
- Data quality

Mục tiêu:

> Không bỏ sót những thứ con người đã biết là quan trọng.

---

# 2. Không để rubric trở thành toàn bộ analysis

Rubric giải quyết **known knowns**.

Nhưng analyst còn phải tìm:

**unknown unknowns**.

Nếu prompt chỉ nói:

> “Hãy phân tích theo 8 mục này”

thì ta đang chủ động giới hạn search space của LLM.

Vì vậy playbook này không dùng:

`Rubric → Report`

mà dùng hai lane độc lập:

```text
                    BUSINESS CONTEXT
                           +
                    VERIFIED DATA
                           │
               ┌───────────┴───────────┐
               │                       │
               ▼                       ▼
        CONTROL LANE              DISCOVERY LANE
        known questions           open questions
        known KPIs                anomalies
        known risks               segments
        rubric                    hypotheses
               │                       │
               └───────────┬───────────┘
                           ▼
                       VERIFY
                           ▼
                       CHALLENGE
                           ▼
                       SYNTHESIZE
```

### Classification

**Synthesis của playbook này.**

Không phải một câu Karpathy đã tuyên bố.

---

# 3. Discovery phải là iterative loop

## Evidence: InsightBench / AgentPoirot

InsightBench đánh giá LLM data-analysis agents trên khả năng tạo ra insight chứ không chỉ trả lời câu hỏi có sẵn.

Agent workflow bao gồm:

- generate analysis questions;
- analyze;
- extract insight;
- generate follow-up questions;
- select next question;
- continue analysis;
- synthesize results.

Điểm quan trọng:

> Analysis được model như một vòng lặp khám phá, không phải một lần prompt → answer. citeturn628493search0


## Analyst translation

Discovery lane nên chạy:

```text
Observe
   ↓
Generate candidate questions
   ↓
Test
   ↓
Find signal
   ↓
Generate follow-up hypothesis
   ↓
Test again
   ↓
Stop when marginal insight becomes low
```

Không nên:

```text
Read dashboard
   ↓
Write interesting paragraph
```

---

# 4. LLM tạo giả thuyết; tool xác minh

LLM phù hợp với:

- hiểu semantic;
- đặt câu hỏi;
- tạo hypothesis;
- chọn segmentation;
- đề xuất phép kiểm tra;
- viết SQL/Python;
- interpret outputs;
- tạo follow-up question;
- viết narrative.

LLM không nên là source-of-truth cho:

- SUM;
- COUNT;
- percentile;
- growth rate;
- statistical test;
- exact ranking;
- reconciliation;
- anomaly threshold.

Rule:

> **Numerical fact must come from deterministic computation whenever practical.**

Flow:

```text
LLM hypothesis
      ↓
SQL / Python / BI engine
      ↓
result
      ↓
LLM interpretation
```

Không phải:

```text
raw data
   ↓
LLM mentally calculates
   ↓
claim
```

---

# 5. Business semantics đi trước analysis

LLM không thể phân tích tốt nếu chỉ hiểu column names.

Input tối thiểu nên có:

## Business context

- business model;
- current priorities;
- important processes;
- known risks;
- what management currently cares about.

## Semantic contract

Ví dụ:

```text
GMV:
gross transaction value before refunds

Active customer:
customer with >= 1 settled transaction in period

Failed payment:
terminal failed status, excluding user-cancelled
```

## Data metadata

- tables;
- dimensions;
- grain;
- freshness;
- known quality limitations.

Rule:

> **Không cho model tự suy diễn business meaning từ tên cột nếu meaning ảnh hưởng kết luận.**

---

# 6. Control Lane — Rubric-driven analysis

Control lane trả lời:

> Những điều chúng ta bắt buộc không được bỏ sót tuần này là gì?

Ví dụ:

```text
Revenue
Margin
Volume
Conversion
Retention
Forecast variance
SLA
Known incidents
Data quality
```

Rubric có thể định nghĩa:

- metric;
- definition;
- expected range;
- comparison baseline;
- alert condition;
- materiality threshold.

Ví dụ:

```text
Metric: Payment Success Rate

Definition:
successful settled payments / eligible payment attempts

Compare:
WoW, 4-week baseline

Investigate:
absolute movement > 2pp

Must segment:
country, payment method, platform
```

Control lane ưu tiên:

**coverage + consistency**.

Không ưu tiên creativity.

---

# 7. Discovery Lane — Open exploration

Discovery lane không được bắt đầu bằng toàn bộ rubric.

Nó nhận:

- business semantics;
- data metadata;
- available dimensions;
- current period;
- historical baseline;
- known exclusions.

Prompt intent:

> Find material, unusual, unexplained or potentially actionable patterns that are not already obvious from the standard scorecard.

Workflow:

```text
Generate candidate questions
        ↓
Rank by potential materiality
        ↓
Test top candidates
        ↓
Segment meaningful signals
        ↓
Generate competing explanations
        ↓
Attempt falsification
        ↓
Retain only supported findings
```

Discovery output có thể gồm:

- anomaly;
- new segment behavior;
- structural shift;
- relationship worth investigation;
- suspected root cause;
- hypothesis needing more evidence.

Important:

> Hypothesis ≠ finding.

---

# 8. Evidence hierarchy

Mỗi insight nên được classify:

## OBSERVATION

Data trực tiếp cho thấy điều gì?

Ví dụ:

> Payment success rate giảm từ 94.1% xuống 88.7%.

## PATTERN

Breakdown cho thấy movement tập trung ở đâu?

> 82% của decline đến từ Android / PH / payment method X.

## HYPOTHESIS

Giải thích khả dĩ là gì?

> Có thể liên quan rollout app version 8.4.

## VERIFIED EXPLANATION

Có evidence độc lập hỗ trợ causal/explanatory claim?

> Version 8.4 rollout bắt đầu cùng thời điểm và failure code X tăng tương ứng.

## RECOMMENDATION

Action nào hợp lý dựa trên evidence hiện có?

Không được collapse:

```text
Observation
   ↓
immediately
   ↓
Root cause
```

---

# 9. Challenge pass

Một analysis chưa hoàn thành khi analyst đầu tiên thấy nó hợp lý.

Phải có một pass độc lập hỏi:

- Có explanation khác không?
- Có seasonality không?
- Aggregation có che Simpson's paradox không?
- Segment này đủ sample không?
- Data freshness có vấn đề không?
- Đây là correlation hay causation?
- Baseline có phù hợp không?
- Có metric definition change không?
- Có evidence nào contradict finding không?

Output:

```text
SUPPORTED
WEAK
REJECT
NEEDS MORE DATA
```

---

# 10. Karpathy's LLM Council — dùng ở đâu?

## Source

`llm-council` của Karpathy chạy ba stage:

1. nhiều LLM trả lời độc lập;
2. các LLM review/rank các answer khác trong trạng thái anonymized;
3. một Chairman synthesize final answer.

Karpathy mô tả ranking theo **accuracy and insight**. citeturn628493search0turn628493search2


Ông cũng nói repo này là một experimental Saturday hack và không định maintain nó.

Vì vậy playbook này **reuse methodology, không phụ thuộc implementation code của repo**. citeturn628493search2

---

# 11. Council không chạy toàn bộ analyst pipeline

Không dùng:

```text
5 models
 ×
every query
 ×
every metric
 ×
every week
```

Quá tốn và phần lớn không cần thiết.

Council nên là **escalation mechanism**.

Default:

```text
Primary Analyst
      ↓
Deterministic Verification
      ↓
Independent Reviewer
      ↓
Final synthesis
```

Escalate sang Council khi:

- high-stakes decision;
- surprising finding;
- ambiguous root cause;
- strategic recommendation;
- models disagree strongly;
- analyst confidence thấp;
- finding có thể dẫn đến action tốn kém.

---

# 12. Council mode cho analyst

Adapt methodology từ Karpathy:

```text
                VERIFIED FINDING PACKAGE
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Reviewer A      Reviewer B      Reviewer C
     evidence        alternative     materiality
     quality         explanation     / actionability
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                ANONYMOUS REVIEW
                         ▼
                    SYNTHESIS
```

Các reviewers nên độc lập trước khi thấy output của nhau.

Sau đó anonymous review mới xảy ra.

Lý do lấy từ council methodology:

> Independence trước, critique sau. citeturn628493search0


---

# 13. Không nhất thiết reviewers phải có persona cố định

Karpathy original chủ yếu dùng **different models**, không phải hệ persona.

Các community adaptations sau này thêm:

- contrarian;
- first-principles;
- executor;
- outsider;
- expansionist.

Đó là adaptation của cộng đồng, không phải original Karpathy method. citeturn628493search9turn628493search12

Playbook này không bắt buộc personas.

Ưu tiên:

```text
independent analysis
+
different model/model family when economically reasonable
+
anonymous review
```

Persona chỉ là optional diversity mechanism.

---

# 14. Materiality gate

Không phải anomaly nào cũng đáng viết report.

Mỗi finding nên được chấm tối thiểu theo:

```text
Magnitude
Business impact
Confidence
Persistence
Actionability
Novelty
```

Điểm này là **design synthesis của playbook**, không phải Karpathy standard.

Mục tiêu:

> tránh report biến thành danh sách anomaly dài nhưng vô dụng.

Có thể dùng rubric cho bước này vì đây là **judgment lặp lại**, đúng kiểu problem mà explicit scoring methodology xử lý tốt.

---

# 15. Final synthesis

Weekly report không được phản ánh “mọi thứ model thấy”.

Nó chỉ chứa:

## 1. What changed?

Verified observations.

## 2. Why does it matter?

Business materiality.

## 3. What likely explains it?

Supported explanation hoặc explicit hypothesis.

## 4. What did discovery find?

Insight ngoài standard scorecard.

## 5. What remains uncertain?

Missing evidence / competing explanations.

## 6. What should we do?

Action hoặc investigation.

---

# 16. Full LLM Analyst Flow

```text
BUSINESS CONTEXT
       +
SEMANTIC CONTRACT
       +
DATA / METADATA
       │
       ▼
UNDERSTAND
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
CONTROL LANE            DISCOVERY LANE
Rubric                   Open exploration
Known KPIs               Generate questions
Known risks              Hypotheses
Expected checks          Segmentation
       │                     │
       └──────────┬──────────┘
                  ▼
             VERIFY
         SQL / Python / tools
                  │
                  ▼
         EVIDENCE CLASSIFY
 Observation / Pattern /
 Hypothesis / Verified explanation
                  │
                  ▼
             CHALLENGE
       Independent reviewer
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
 normal finding       high stakes /
                     major uncertainty
                            │
                            ▼
                       LLM COUNCIL
                            │
                            ▼
                    MATERIALITY GATE
                            │
                            ▼
                      SYNTHESIS
                            │
                            ▼
                    WEEKLY REPORT
```

---

# 17. Traceability requirement

Mọi important conclusion phải trace được:

```text
Report claim
   ↓
Finding
   ↓
Query / computation
   ↓
Source table / dataset
   ↓
Metric definition
   ↓
Business meaning
```

Nếu chain bị đứt:

**không nâng hypothesis thành conclusion.**

---

# 18. Những thứ playbook cố tình không làm

Không:

- bắt LLM fill report template ngay khi nhận data;
- dùng rubric làm giới hạn discovery;
- tin calculation của LLM nếu tool có thể tính;
- gọi anomaly là insight ngay lập tức;
- gọi correlation là root cause;
- sử dụng multi-agent chỉ để trông sophisticated;
- để Chairman synthesize evidence chưa verify;
- ép mọi business vào cùng một scorecard.

---

# 19. Source → Principle → Implementation Trace

| Source | Lesson giữ lại | Implementation trong playbook |
|---|---|---|
| Karpathy `jobs` | Explicit scoring methodology cho fuzzy repeated judgment | Control rubric + materiality scoring |
| Karpathy `jobs` | LLM làm việc trên source-grounded structured context | Business semantics + verified evidence |
| Karpathy `llm-council` | Independent first opinions | Independent challenge/council passes |
| Karpathy `llm-council` | Anonymous peer review | Council review stage |
| Karpathy `llm-council` | Rank on accuracy + insight | Reviewer criteria |
| Karpathy `llm-council` | Chairman synthesis | Final council synthesis |
| InsightBench / AgentPoirot | Analysis là iterative question → insight → follow-up loop | Discovery lane |
| Analyst engineering principle | Deterministic computation cho quantitative truth | SQL/Python verification |
| **Our synthesis** | Rubric và discovery chạy song song | Two-lane architecture |
| **Our synthesis** | Council chỉ là escalation path | Cost-efficient challenge architecture |
| **Our synthesis** | Evidence maturity: observation → pattern → hypothesis → verified explanation | Finding classification |
| **Our synthesis** | Materiality gate trước report | Prevent noisy weekly reports |

---

# 20. First principle của playbook

Nếu phải nhớ một câu:

> **Use structure to prevent known mistakes, preserve openness to discover unknowns, and never let language-model confidence substitute for evidence.**

Hay dưới dạng pipeline:

```text
CONTEXT
  ↓
EXPLORE
  ↓
COMPUTE
  ↓
VERIFY
  ↓
CHALLENGE
  ↓
SYNTHESIZE
```

Rubric là guardrail.

Discovery là search.

SQL/Python là calculator.

Council là critic.

LLM là reasoning interface.

Evidence mới là source of truth.