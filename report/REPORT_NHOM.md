# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G48
**Thành viên: Dương Đạt Khang, Tạ Việt Cương, Chung Văn Duy
**Ngày:** 19/09/2026**

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Học bổng UEH và chính sách hỗ trợ sinh viên

**Tại sao nhóm chọn chủ đề này?**

> Chúng tôi chọn chủ đề học bổng vì đây là tài liệu có tính thời sự, dễ xác minh bằng nguồn chính thức, và đa dạng ở nhiều khối học lực, đối tượng và mốc thời gian. Với bộ dữ liệu này, nhóm có thể kiểm tra cả retrieval theo chủ đề lẫn khả năng filter theo `audience` và `department`, phù hợp với bài lab về embedding và vector store.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
| - | --------------- | ------------------- | ------------------------ | ----------- | ------------------ |
| 1 | undergraduate-scholarship-page.md | student.ueh.edu.vn | 2026-09-19 | Khoảng 8–10k | audience, source_url, retrieved_at, doc_id, department |
| 2 | undergraduate-scholarship.md | student.ueh.edu.vn | 2026-09-19 | Khoảng 8–10k | audience, source_url, retrieved_at, doc_id, department |
| 3 | undergraduate-scholarship-info.md | student.ueh.edu.vn | 2026-09-19 | Khoảng 8–10k | audience, source_url, retrieved_at, doc_id, department |
| 4 | graduate-scholarship.md | student.ueh.edu.vn | 2026-09-19 | Khoảng 8–10k | audience, source_url, retrieved_at, doc_id, department |
| 5 | masters-science-technology-scholarship.md | student.ueh.edu.vn | 2026-09-19 | Khoảng 8–10k | audience, source_url, retrieved_at, doc_id, department |
| 6 | masters-scholarship.md | student.ueh.edu.vn | 2026-09-19 | Khoảng 8–10k | audience, source_url, retrieved_at, doc_id, department |
| 7 | student-support-page.md | student.ueh.edu.vn | 2026-09-19 | Khoảng 8–10k | audience, source_url, retrieved_at, doc_id, department |
| 8 | student-financial-aid.md | student.ueh.edu.vn | 2026-09-19 | Khoảng 8–10k | audience, source_url, retrieved_at, doc_id, department |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [X] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [X] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
| ----------------- | ----- | ----------------- | ---------------------------------------------- |
| audience | string | student | Phân loại đối tượng chính để lọc câu hỏi theo sinh viên, cán bộ, hay phụ huynh |
| source_url | string | https://student.ueh.edu.vn/... | Truy vết nguồn gốc và giúp kiểm chứng provenance |
| retrieved_at | string | 2026-09-19 | Ghi ngày thu thập, giúp theo dõi tính thời sự |
| document_version | string | 2026.09 | Cho phép so sánh phiên bản tài liệu khác nhau |
| department | string | finance / scholarship / graduate | Giảm nhiễu khi nhiều tài liệu cùng chủ đề nhưng khác đơn vị |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy)           | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
| ---------- | ---------------------------------- | ----------------- | --------------------- | ------------------------------- |
| student-financial-aid.md | FixedSizeChunker (`fixed_size`) | ~12 | ~480 ký tự | Có, nhưng bị cắt ở ranh giới dữ liệu quan trọng |
| student-financial-aid.md | SentenceChunker (`by_sentences`) | ~10 | ~560 ký tự | Có, dễ đọc hơn và giữ mốc thời gian tốt hơn |
| graduate-scholarship.md | RecursiveChunker (`recursive`) | ~8 | ~650 ký tự | Có, phù hợp với bảng điều kiện và phần header dài |

### Chiến lược của từng thành viên

**Thành viên 1 — Dương Đạt Khang**

- **Loại chiến lược:** FixedSizeChunker + metadata filter theo audience
- **Mô tả & lý do chọn cho chủ đề này:** Fixed-size giúp nguyên tắc tách văn bản đều, dễ kiểm tra và so sánh. Với học bổng, filter theo `audience` rất quan trọng vì nhiều trang có đề cập đến cùng chủ đề nhưng khác đối tượng.
- **Code snippet (nếu custom):**

```python
store.search_with_filter(question, top_k=3, metadata_filter={"audience": "student"})
```

**Thành viên 2 — Tạ Việt Cương**

- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Sentence chunking giữ được câu hoàn chỉnh và mốc thời gian quan trọng như ngày đăng ký, điểm, tín chỉ. Với dữ liệu chính sách, lấy nguyên câu sẽ giúp answer generation ít hiểu nhầm hơn.
- **Code snippet (nếu custom):**

```python
SentenceChunker(max_sentences_per_chunk=3)
```

**Thành viên 3 — Chung Văn Duy**

- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Học bổng có nhiều bảng, heading và mục nhỏ; recursive chunker rất hiệu quả để giữ từng section và tránh trộn nội dung khác nhau trong cùng một tài liệu.
- **Code snippet (nếu custom):**

```python
RecursiveChunker(chunk_size=500, separators=["\n\n", "\n", ". ", " "])
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
| ------------ | ------------------------ | ----------------------- | ------------ | ----------- |
| Dương Đạt Khang | FixedSize + filter | 0/10 | dễ triển khai, filter rõ đối tượng | dễ cắt mất dữ liệu trong bảng điều kiện |
| Tạ Việt Cương | SentenceChunker | 0/10 | giữ câu nguyên văn tốt | nếu câu quá dài có thể chia không đồng nhất |
| Chung Văn Duy | RecursiveChunker | 0/10 | giữ cấu trúc section tốt | vẫn bị ảnh hưởng bởi mock embeddings |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> Cách tốt nhất cho chủ đề học bổng là sự kết hợp giữa `RecursiveChunker` và `metadata_filter` theo `audience`. Chính sách học bổng thường có cấu trúc header + bảng + điều kiện; recursive giữ được cấu trúc, còn filter giúp loại tài liệu không phù hợp với đối tượng. Tuy nhiên, trong benchmark hiện tại, chất lượng còn phụ thuộc rất lớn vào backend embedding và mock embedding đã phá vỡ độ tin cậy của ranker.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
| - | ----------------- | ----------------------------------- | ---------------------------- |
| 1 | Sinh viên ĐHCQ khóa 48, 49, 50, 51 đăng ký online học bổng Hỗ trợ học tập HKĐ2026 từ ngày nào đến ngày nào? | Từ 25/3/2026 đến 08/4/2026, không lấy 07/4/2026 làm mốc đăng ký chính thức. | `undergraduate-scholarship-page` |
| 2 | Song ngành Công nghệ truyền thông và Kinh doanh quốc tế K50 cần tối thiểu bao nhiêu tín chỉ? | 14 tín chỉ; các chương trình còn lại là 15 tín chỉ trong HKC2025. | `graduate-scholarship` |
| 3 | Học bổng VAS năm 2026 hỗ trợ bao nhiêu học phí và yêu cầu điểm nào? | 100% học phí; điểm TB 2,5; điểm rèn luyện từ 65; chưa nhận học bổng khác. | `masters-science-technology-scholarship` |
| 4 | Học bổng ngành Toán học kỳ I năm 2026–2027 có giá trị và số suất bao nhiêu? | 26.125.000 đồng mỗi lần xét; 150 suất; hạn đăng ký 09/09/2026. | `student-financial-aid` |
| 5 | Theo thông báo học bổng HKC2026 dành cho K52, thời gian đăng ký online và nộp hồ sơ bản cứng là khi nào? | Đăng ký online 17/8–02/9/2026; nộp bản cứng 04/9 và 07/9/2026. | `masters-scholarship` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
| - | --------- | -------------------------------------- | --------------------------------- | -------- |
| 1 | Q1 | Recursive + filter student | Không | Top-3 lệch sang policy staff và tài liệu không chứa evidence chính xác |
| 2 | Q2 | SentenceChunker | Không | Tổng số tín chỉ nằm ở bảng nhưng không lọt top-3 khi lấy ranking với mock embedding |
| 3 | Q3 | RecursiveChunker | Không | Khó tìm điểm rèn luyện và điều kiện học phí do top-k trôi theo chủ đề |
| 4 | Q4 | FixedSize + filter student | Không | Thêm filter không giúp vì gold doc chỉ có ở top-3 bằng may rủi, không có evidence đúng |
| 5 | Q5 | SentenceChunker | Không | Mốc ngày đăng ký và nộp hồ sơ bị các tài liệu khác lấn top-3 |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Metadata filter có ích khi câu hỏi yêu cầu phân biệt `audience` như Q1, Q4 và Q5. Tuy nhiên, trong benchmark hiện tại, nó không đủ để cứu retrieval vì mock embedding không biết ngữ nghĩa và thực sự làm hỏng rank order. Kết quả A/B cho thấy với Q1, filter student đã làm các doc đúng đối tượng ra khỏi lợi thế, nhưng không đem lại top-3 chứa câu trả lời đúng. Điều này chứng tỏ filter là cần thiết nhưng không thay thế được chất lượng embedding và chunking.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

> - Mock embedding làm hỏng benchmark vì hash MD5 không biểu diễn ngữ nghĩa; top-k có thể rất khác với thực tế.
> - Filter theo metadata tuy cần thiết nhưng chỉ hữu ích nếu câu hỏi thực sự cần phân biệt đối tượng hoặc đơn vị.
> - Chunker và section structure ảnh hưởng mạnh đến khả năng tìm đúng evidence; tableau chính sách dễ bị tráo do sai section hoặc thiếu overlap.

**Bài học rút ra khi so sánh trong nhóm:**

> Cùng một bộ tài liệu nhưng chiến lược khác nhau dẫn tới mức độ ổn định retrieval khác nhau. Fixed-size giúp dễ triển khai, sentence giữ câu nguyên văn tốt, recursive giữ cấu trúc bảng tốt hơn, nhưng khi backend là mock thì tất cả đều bị xáo trộn bởi ranking không có semantic meaning. Điều này cho thấy benchmark chỉ đáng tin khi có embedding thực và evidence nội dung được kiểm tra kỹ.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nếu làm lại, nhóm sẽ ưu tiên dùng embedding thật, giảm rủi ro từ mock, và chọn chunker theo cấu trúc section có overlap phù hợp để giữ cả header lẫn dữ liệu. Đồng thời, nhóm sẽ rà soát lại câu hỏi benchmark để đảm bảo mỗi câu hỏi có thể “có đủ evidence” trong một tài liệu và không bị trộn với các thông tin chiều ngang khác.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                   | Điểm tự đánh giá |
| -------------------------------------------- | ---------------------- |
| Lựa chọn tài liệu (Document Set Quality) | 8 / 10                   |
| Thiết kế chiến lược (Strategy Design)   | 10 / 15                   |
| Chất lượng truy xuất (Retrieval Quality) | 0 / 10                   |
| Thuyết trình (Demo)                        | 5 / 5                    |
| **Tổng phần nhóm**                  | **23 / 40**         |

> Số điểm này phản ánh thực tế benchmark trên mock embedder: code và pipeline cơ bản là đúng, nhưng retrieval quality với semantic noise bị đánh thấp theo đúng tiêu chí của bài lab.
