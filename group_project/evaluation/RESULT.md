# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-25 |
| Framework and version              | RAGAS 0.4.3 / LangChain 1.4.2 |
| Evaluator model                    | GPT-4o-mini |
| Generator model                    | GPT-4o-mini |
| Embedding model                    | BAAI/bge-m3 |
| Corpus version/commit              | branch/giap |
| Golden dataset size                | 15 cases |
| `top_k`                            | 5 |
| Fallback threshold and calibration | 0.3 (calibrated on in-domain / out-of-domain) |

## Configurations

- **Config A — dense-only:** ChromaDB cosine similarity retrieval, top_k=5, without lexical search or RRF.
- **Config B — hybrid + RRF:** ChromaDB dense search + BM25Okapi lexical search, merged via Reciprocal Rank Fusion (k=60), top_k=5, fallback on threshold < 0.3.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |     0.87 |     0.94 |     +0.07 |
| Answer relevance  |     0.84 |     0.91 |     +0.07 |
| Context recall    |     0.80 |     0.93 |     +0.13 |
| Context precision |     0.82 |     0.89 |     +0.07 |
| **Average**       |    0.833 |    0.918 |    +0.085 |

## A/B comparison

- Cấu hình tốt hơn: Config B (Hybrid + RRF).
- Evidence: Config B vượt trội hơn Config A ở toàn bộ các metric, đặc biệt là Context Recall (+13%) và Faithfulness (+7%). BM25 giúp bắt chính xác các keyword đặc thù, mã định danh ngành (7460108), số quyết định (474/2025/QĐ-VUNI) và thuật ngữ chuyên ngành mà dense embedding thuần có thể bỏ lỡ hoặc rank thấp. RRF (k=60) cân bằng hiệu quả thứ hạng mà không làm méo mó phân phối điểm cosine gốc.
- Trade-off về latency/cost: Config B tốn thêm chi phí tính toán BM25 và RRF (~12ms latency), nhưng không tốn thêm API token embedding hay LLM generation so với Config A. Chất lượng context tăng rõ rệt giúp giảm hallucination của LLM và tăng độ tin cậy của citation.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Sinh viên xem danh sách các lớp học phần đã đăng ký thành công ở vị trí nào? | Config A | 0.65 | 0.70 | 0.60 | 0.60 | retrieval | Dense model nhầm lẫn giữa các màn hình hướng dẫn trong handbook do câu ngắn |
|   2 | Mã chương trình đào tạo của ngành Cử nhân Khoa học Dữ liệu là gì? | Config A | 0.70 | 0.75 | 0.50 | 0.55 | retrieval | Dense embedding không hiểu tốt chuỗi số mã ngành (7460108) nếu không có BM25 |
|   3 | Sinh viên có thể nộp học phí theo những hình thức nào? | Config B | 0.85 | 0.88 | 0.80 | 0.82 | generation | Model tóm tắt ngắn gọn nhưng sót chi tiết nộp qua cổng Salesforce |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Bổ sung metadata filter cho handbook hướng dẫn sinh viên | Case 1 bị lẫn lộn giữa các bước trong handbook đăng ký tín chỉ | Tăng context precision từ 0.89 lên 0.95 cho các tài liệu thủ tục | Đánh giá lại recall/precision trên các câu hỏi quy trình sinh viên |
|        2 | Duy trì Hybrid Search (BM25 + Dense) làm mặc định | Case 2 cho thấy dense-only thất bại với mã số và số quyết định | Khắc phục hoàn toàn lỗi truy vấn thực thể số và mã định danh | Chạy test case trên các query chứa số quyết định hoặc mã ngành |
|        3 | Cải tiến system prompt để bắt buộc trích xuất đủ các phương án liệt kê | Case 3 sót phương án thanh toán thứ hai khi câu trả lời có nhiều gạch đầu dòng | Tăng faithfulness và completeness của câu trả lời | Đánh giá metric faithfulness và answer completeness trên golden set |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Document Reordering (Lost-in-the-middle) | Sequential context | +0.03 Faithfulness | +0.1ms / $0 | Reordering giúp LLM chú ý tốt hơn các chunk quan trọng đặt ở đầu và cuối prompt |
