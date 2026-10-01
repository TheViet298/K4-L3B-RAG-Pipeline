# Individual contribution report

## Thông tin

- Họ và tên: Ngô Thế Việt
- Mã học viên: 02594
- Nhóm: K4-L3B Group
- Repository/branch: main (TheViet298/K4-L3B-RAG-Pipeline)

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Thu thập tài liệu pháp lý & tin tức (Task 1 & Task 2) | Thu thập các tài liệu cẩm nang sinh viên, khung CTĐT VinUni và triển khai module thu thập dữ liệu với cơ chế fallback tự động | `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py`, `data/landing/` | Done |
| Chuẩn hóa dữ liệu (Task 3) | Hỗ trợ pipeline trích xuất Markdown từ tài liệu pháp lý (MarkItDown) và tin tức, bổ sung metadata chuẩn | `src/task3_convert_markdown.py`, `data/standardized/` | Done |
| Xây dựng Golden Dataset & Đánh giá (Task 9 & Evaluation) | Thiết kế tập câu hỏi - đáp ground-truth (15 Q&A), tham gia chạy thử nghiệm A/B đánh giá 4 metrics và phân tích failure case | `group_project/evaluation/golden_dataset.json`, `group_project/evaluation/RESULT.md` | Done |
| Tích hợp Chatbot UI & Quản trị Repository | Quản trị repository, review và merge Pull Request #1 (`branch/giap`), kiểm thử toàn diện 20/20 tests và hoàn thiện Streamlit UI | `app.py`, `tests/`, PR #1 | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Bổ sung cơ chế Fallback bằng BeautifulSoup + Requests cho Task 2 bên cạnh Crawl4AI.  
   - **Lý do/evidence:** Thư viện Crawl4AI phụ thuộc chặt vào Playwright và Chromium headless browser, dễ phát sinh lỗi hoặc gián đoạn môi trường trong một số hệ điều hành / sandbox không có kết nối ngoài. Sử dụng `requests` kèm parser `BeautifulSoup` và headers giả lập trình duyệt giúp quá trình crawl tin tức tuyển sinh VinUni diễn ra tức thì, ổn định và độc lập với browser engine.  
   - **Trade-off:** Không thực thi được các trang render hoàn toàn bằng dynamic client-side JavaScript phức tạp, nhưng đối với các trang FAQ tuyển sinh của VinUni thì HTML tĩnh đã chứa đầy đủ dữ liệu.

2. **Quyết định:** Hiệu chỉnh ngưỡng Cosine Fallback (`SCORE_THRESHOLD = 0.3`) dựa trên Dense Cosine gốc thay vì điểm sau RRF.  
   - **Lý do/evidence:** Điểm RRF phản ánh thứ bậc xếp hạng tương đối giữa dense và lexical search, không mang ý nghĩa độ tương đồng ngữ nghĩa tuyệt đối. Bằng cách giữ nguyên Cosine Score gốc của Semantic Search để so sánh với threshold 0.3, pipeline phát hiện chính xác các câu hỏi ngoài domain (out-of-domain) để kích hoạt PageIndex fallback an toàn.  
   - **Trade-off:** Cần truyền song song điểm dense gốc qua pipeline thay vì chỉ dùng danh sách sau RRF.

## Kiểm thử và kết quả

- **Test hoặc query đã dùng:**
  - Chạy toàn bộ test suite tự động: `pytest tests/test_contracts.py -q` (15/15 pass) và `pytest tests/test_acceptance.py -q` (5/5 pass). Toàn bộ 20/20 tests passed.
  - Kiểm thử tương tác trực tiếp trên Streamlit Chatbot (`streamlit run app.py`) với các câu hỏi in-domain ("Điều kiện tuyển sinh VinUni", "Quy trình nộp đơn sớm") và câu hỏi ngoài domain để kiểm tra safe refusal & citation.
- **Kết quả trước/sau:** Pipeline hoạt động trơn tru từ khâu nạp tài liệu, chia chunk, truy vấn hybrid đến tổng hợp câu trả lời kèm citation rõ ràng [Document X | Source].
- **Lỗi đã phát hiện và cách xử lý:** Phát hiện lỗi encoding `UnicodeEncodeError (cp1252)` trên môi trường Windows console khi in tiếng Việt từ `task1`; đã chuẩn hóa thông điệp console dạng ASCII thân thiện. Đồng thời xử lý metadata trong ChromaDB để tránh lỗi binding khi trường `url` nhận giá trị null.

## Điều còn hạn chế

- **Một hạn chế cụ thể:** Hệ thống hiện tại mới lưu trữ lịch sử hội thoại trên giao diện Streamlit (session state) mà chưa đưa context hội thoại nhiều lượt (Multi-turn conversation memory) vào prompt của LLM.
- **Nếu có thêm thời gian:** Tích hợp Conversation Memory và Query Rewriting (viết lại câu hỏi người dùng dựa trên ngữ cảnh các lượt hỏi trước) để hỗ trợ tốt hơn các câu hỏi follow-up.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 27/09/2026
- Tên thành viên: Ngô Thế Việt
