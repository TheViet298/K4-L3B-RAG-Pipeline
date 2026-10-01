# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Quang Đạo (2A202602394)
- Mã học viên: 2A202602394
- Nhóm: K4-L3B Group
- Repository/branch: main / branch/dao

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Thu thập dữ liệu (Task 1 & 2) | Thu thập và thẩm định 4 PDF chính sách quy chế và 5 JSON tin tức tuyển sinh, dịch vụ sinh viên với 100% URL thật từ domain `vinuni.edu.vn` | `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py` | Done |
| Chuẩn hoá Markdown (Task 3) | Viết pipeline chuyển đổi văn bản sang Markdown chuẩn, bảo toàn cấu trúc bảng biểu, điều khoản và metadata header URL/Title | `src/task3_convert_markdown.py`, `data/standardized/` | Done |
| Chunking & Indexing (Task 4) | Thiết lập RecursiveCharacterTextSplitter (500 ký tự, overlap 50), vector hóa embedding và upsert vào ChromaDB persistent | `src/task4_chunking_indexing.py`, `chroma_db/` | Done |
| Hybrid Retrieval (Task 5 & 6) | Xây dựng Semantic Search với ChromaDB và BM25Plus Lexical Search giải quyết triệt để lỗi Zero-IDF trên tập văn bản nhỏ | `src/task5_semantic_search.py`, `src/task6_lexical_search.py` | Done |
| Reranking & Fallback (Task 7, 8, 9) | Cài đặt Reciprocal Rank Fusion ($k=60$), kiểm soát ngưỡng Cosine gốc (`SCORE_THRESHOLD = 0.35`) và fallback an toàn sang PageIndex | `src/task7_reranking.py`, `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` | Done |
| Generation & Citation (Task 10) | Kỹ thuật Reordering chống lost-in-the-middle, định dạng context có Title/Source, trích xuất citation nguồn và safe refusal | `src/task10_generation.py` | Done |
| Giao diện Chatbot & Bonus (UI) | Phát triển giao diện Streamlit hiện đại, tích hợp Conversation Memory cho câu hỏi follow-up và Source Highlighting trực quan | `app.py` | Done |
| Bonus Reranker & Expansion | Xây dựng module mở rộng từ khóa viết tắt VinUni (`bonus_query_expansion.py`) và Neural Cross-Encoder Reranker (`bonus_advanced_reranker.py`) | `src/bonus_query_expansion.py`, `src/bonus_advanced_reranker.py` | Done |
| Evaluation & Golden Dataset | Xây dựng 15 Golden Q&A chuẩn mực, chạy kiểm thử đo lường 4 metrics Ragas, đối sánh A/B và lập báo cáo `RESULT.md` | `group_project/evaluation/`, `reports/RESULT.md` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng thuật toán `BM25Plus` thay cho `BM25Okapi` tiêu chuẩn trong module lexical search (`src/task6_lexical_search.py`).  
   - **Lý do/evidence:** Với công thức BM25Okapi truyền thống, IDF được tính theo $\ln\left(\frac{N - n + 0.5}{n + 0.5}\right)$. Trên một corpus kích thước vừa phải hoặc khi từ khóa xuất hiện ở tỷ lệ tài liệu lớn hơn một nửa ($n > N/2$), điểm IDF sẽ nhận giá trị $\le 0$. Điều này dẫn tới việc BM25Okapi gán điểm $0.0$ cho các tài liệu thực sự chứa từ khóa truy vấn, khiến test contract thất bại. BM25Plus bổ sung một hằng số cận dưới $\delta = 1.0$, đảm bảo mọi tài liệu có chứa từ khóa đều nhận điểm số dương hợp lệ.  
   - **Trade-off:** Điểm số BM25Plus có dải giá trị dịch chuyển lên một khoảng cố định, tuy nhiên do hệ thống sử dụng xếp hạng thứ bậc (rank-based) thông qua RRF thay vì cộng trực tiếp score nên sự dịch chuyển này không ảnh hưởng đến trật tự tương đối mà còn giúp thứ hạng ổn định hơn.

2. **Quyết định:** Giữ nguyên Cosine Similarity gốc từ Semantic Search để kiểm tra ngưỡng Fallback (`SCORE_THRESHOLD = 0.35`) thay vì dùng điểm dung hợp sau RRF.  
   - **Lý do/evidence:** Thuật toán RRF chuẩn hóa theo công thức $\sum \frac{1}{k + \text{rank}_i}$, điểm đầu ra bị bó hẹp trong dải giá trị rất nhỏ (khoảng $0.01 - 0.033$) và phụ thuộc vào số lượng danh sách xếp hạng tham gia dung hợp chứ không phản ánh độ tương đồng ngữ nghĩa thực sự giữa câu hỏi và tài liệu. Dùng điểm cosine distance chuyển đổi sang similarity $\max(0.0, 1.0 - \text{distance})$ phản ánh trực tiếp câu hỏi có nằm trong miền tri thức (in-domain) hay ngoài miền (out-of-domain).  
   - **Trade-off:** Pipeline cần truyền kèm điểm dense gốc cùng với kết quả tìm kiếm dense để hàm `retrieve()` có thể đánh giá trước khi quyết định kích hoạt fallback sang PageIndex.

## Kiểm thử và kết quả

- **Test hoặc query đã dùng:**
  - Bộ kiểm thử tự động `pytest tests/test_contracts.py` (15 test) và `pytest tests/test_acceptance.py` (5 test). Toàn bộ 20/20 test pass.
  - Bộ 15 câu hỏi thực nghiệm trong `golden_dataset.json` kiểm tra độ trung thực (faithfulness), độ liên quan câu trả lời (answer relevance), context recall và context precision.
- **Kết quả trước/sau:**
  - Trước khi tối ưu: Mô hình Dense-only đạt Context Precision 0.82 và Context Recall 0.80.
  - Sau khi tích hợp Hybrid + RRF: Context Precision tăng lên **0.89** (+7%) và Context Recall tăng lên **0.93** (+13%). Điểm Faithfulness đạt **0.94** (+7%).
- **Lỗi đã phát hiện và cách xử lý:**
  - Lỗi WAF Cloudflare khi crawl dữ liệu: Thư viện `requests` mặc định gửi header rỗng bị máy chủ VinUni từ chối với mã lỗi 403 Forbidden. Đã cấu hình bổ sung đầy đủ `User-Agent` chuẩn trình duyệt (Chrome 120.0), `Accept-Language: vi-VN,vi;q=0.9`, xử lý thành công trả về HTTP 200.
  - Lỗi mã hóa ký tự tiếng Việt trên Windows terminal: Khi in kết quả tiếng Việt bị lỗi `charmap codec can't encode character`. Đã xử lý bằng cách cấu hình `sys.stdout.reconfigure(encoding='utf-8')` ngay tại đầu các file module thực thi.

## Điều còn hạn chế

- **Một hạn chế cụ thể:** Hệ thống hiện tại lưu trữ vector tại local ChromaDB, khi mở rộng quy mô dữ liệu lên hàng nghìn tài liệu sẽ cần giải pháp vector database phân tán (như Qdrant, Milvus hoặc Pinecone) để đảm bảo độ trễ tìm kiếm.
- **Nếu có thêm thời gian:** Triển khai thêm cơ chế tự động đánh giá định kỳ bằng Ragas pipeline tự động thông qua CI/CD GitHub Actions khi có tài liệu mới được bổ sung vào kho tri thức.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Quang Đạo
