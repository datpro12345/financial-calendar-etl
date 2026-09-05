# 001 — Model vẫn bịa số dù Fact Pack đã đủ

**Khi:** Phase 1 weekly outlook (W36/2026), OpenRouter free (MiniMax M3, Nemotron Ultra, Ling Flash Fin).  
**Bối cảnh:** Mọi count, clash, F/P/A, `fact_id` đã tính trong `scripts/analyst/fact_pack.py` rồi nhét vào prompt.

## Hiện tượng

Pack **có hoặc không** từng số — 100% ở tầng bảng. Report vẫn xuất hiện số **không phải giá trị của đúng fact_id**:

| Loại | Ví dụ thật | Pack |
|---|---|---|
| Ngưỡng mới | NFP falsify `~30K`, AHE `<0.2%` | NFP F `55K` / P `-23K`; AHE F `0.3%` (`fact_id=2889/2890`) |
| Số tính thêm | `25bp` từ 2.75% − 2.50% | Pack không có field bp |
| Số có nhưng gắn sai | `0.2%` | Có ở PPI tuần sau, không phải cutoff AHE |
| Hành động / giá | `Long EUR/USD`, `target 1.36` | Không có trong mart |

Cite `fact_id=2889/2890/2891` và `2887/2888` rồi vẫn bịa cutoff — ID dùng như footnote, không phải lookup.

## Vì sao vẫn bịa được

LLM không `SELECT forecast WHERE fact_id=2890`. Nó **sinh token** cho câu “có vẻ đúng”.  
Input đủ số ≠ output bị khóa trong tập số đó. Prompt “cấm bịa” là lời nhắc, không phải ràng buộc.

## Cách phòng / khắc phục trong repo

1. **Upstream:** Fact Pack Python — chặn bịa phép cộng (12 red, clash 19:30).  
2. **Prompt + semantics:** contract, `metrics.yml`, `control_interactions.yml`, textbook — chặn bớt **sai nghĩa**.  
3. **Downstream lint:** `scripts/analyst/report_lint.py` — fail nếu `%`/`K`/giá/`Long` không nằm trong pack.  
4. **Trader-in-the-loop:** Reflexivity giá và cắt lệnh — người đọc chart, không giao model.

## Được 100% chưa? Không.

| Vẫn lọt | Lý do |
|---|---|
| Số **tính ra** từ pack (`25bp`, `75%`) | Lint chỉ allowlist literal, chưa cấm mọi phép trừ |
| Số **có ở chỗ khác** trong pack (`0.2%` PPI → AHE) | Allowlist theo file, chưa bind `fact_id` ↔ F/P |
| Narrative không-số (“Fed pause”, tone speech) | Không có token số để bắt |
| Model khác nhau | Ling Fin sạch hơn Ultra; không model nào bind output |

**100% chỉ có** nếu LLM không được viết số: chỉ chọn `fact_id` + `below_forecast`, Python nhét F/P vào template. Chưa làm. Tạm thời: pack + lint + người review ≠ bảo chứng tuyệt đối.
