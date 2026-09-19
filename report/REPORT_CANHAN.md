# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]: Dương Đạt Khang
**Nhóm:** [Tên nhóm]: G48
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> Độ tương tự cosine cao nghĩa là hai vector hướng về cùng một phía trong không gian embedding, tức là chúng có cùng ý nghĩa hoặc cùng khái niệm dù không nhất thiết dùng cùng từ. Khi hai câu có cùng nghĩa nhưng từ vựng khác nhau, vector của chúng sẽ gần nhau theo góc, nên cosine gần 1.

**Ví dụ có độ tương tự CAO:**

- Câu A: "Học sinh đang chuẩn bị cho kỳ thi cuối kỳ."
- Câu B: "Students are preparing for the final exam."
- Tại sao tương đồng: Hai câu nói cùng một ý tưởng nhưng dùng tiếng Việt và tiếng Anh khác nhau; embedding hiểu nghĩa chứ không chỉ so khớp chữ cái.

**Ví dụ có độ tương tự THẤP:**

- Câu A: "Một chiếc xe đang chạy trên đường."
- Câu B: "Trời hôm nay rất nắng và đẹp."
- Tại sao khác: Chúng không cùng chủ đề và không cùng ý nghĩa; vector điểm tới các hướng khác nhau trong không gian semantic.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> Cosine đo góc giữa hai vector, phản ánh sự tương đồng theo hướng nghĩa, còn Euclid đo khoảng cách tuyệt đối trong cùng không gian và dễ bị ảnh hưởng bởi độ dài vector. Với embedding ngữ nghĩa, hướng là thứ quan trọng hơn, vì cùng nghĩa có thể có cùng hướng dù số lượng từ khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> Bước 1: step = chunk_size - overlap = 500 - 50 = 450.
>
> Bước 2: số chunk gần đúng = ceil((10000 - 50) / 450) = ceil(9950 / 450) = ceil(22.11) = 23.
>
> **Đáp án:** khoảng 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> Khi overlap tăng lên 100, step giảm xuống còn 400, nên số chunk tăng lên: ceil((10000 - 100) / 400) = ceil(9900 / 400) = ceil(24.75) = 25 chunks. Overlap lớn giúp giữ ngữ cảnh giữa các chunk, đặc biệt khi chia các văn bản dài hoặc các đoạn quan trọng bị cắt ở ranh giới; tuy nhiên nó làm tăng số chunk và chi phí xử lý.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> Tôi chuẩn hóa khoảng trắng trước khi tách câu, sau đó dùng regex để chia theo vị trí sau dấu câu như ". ", "! ", "? " và ".\n". Cách này giữ được dấu câu ở cuối câu và tránh làm mất thông tin. Với edge case, tôi xử lý text rỗng và tập hợp câu theo `max_sentences_per_chunk`; vẫn có nhược điểm với chữ viết tắt (TS., v.v.) và số thập phân như 3.14 vì regex có thể cắt sai ở những trường hợp đó.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> Thuật toán ưu tiên tách theo separator lớn trước: `\n\n`, `\n`, `. `, , rồi mới đi xuống các separator nhỏ hơn. Nếu mảnh còn dài hơn `chunk_size`, tôi gọi đệ quy tiếp; nếu đã đạt ngưỡng, tôi gom các mảnh liền kề lại cho tới gần `chunk_size` để tránh sinh ra nhiều chunk quá ngắn. Base case gồm: text rỗng, text ngắn hơn hoặc bằng chunk_size, và không còn separator để thử.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> Store chỉ dùng in-memory. `_make_record` sao chép metadata bằng deepcopy, giữ `doc_id` của file gốc và tạo embedding; `_search_records` tính dot product giữa query embedding và embedding của từng record, sắp xếp điểm giảm dần rồi lấy top-k, không đưa vector vào output. Dot product tương ứng cosine khi vector đã được chuẩn hóa như embedder của lab.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> Lọc metadata trước khi sắp xếp điểm để tài liệu không đúng đối tượng không chiếm chỗ top-k; `search_with_filter` và `search` dùng chung logic `_search_records` trên tập hợp candidate khác nhau. `delete_document` xóa mọi record mà `metadata['doc_id']` khớp với file gốc, bao gồm cả chunk con, và trả về `True`/`False` tùy có xóa được gì hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> Agent truy xuất top-k, đánh số từng chunk `[1]`, `[2]` kèm nguồn, `doc_id` và `chunk_id`, rồi gọi `llm_fn` với prompt yêu cầu chỉ dùng context được cung cấp. Nếu không có kết quả hoặc không tìm thấy thông tin trong ngữ cảnh, agent trả lời rõ ràng rằng không tìm thấy dữ liệu thay vì bịa. Nhờ quy định này, câu trả lời có tính traceability và dễ kiểm chứng nguồn.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\khang\Downloads\gitlabVin\K4-DAY07-D-ng-t-Khang-2A202602624\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\khang\Downloads\gitlabVin\K4-DAY07-D-ng-t-Khang-2A202602624
collecting ... collected 50 items

tests/test_document_io.py::test_frontmatter_is_metadata_not_retrieval_content PASSED [  2%]
tests/test_document_io.py::test_plain_document_still_loads PASSED        [  4%]
tests/test_document_io.py::test_broken_frontmatter_fails_explicitly PASSED [  6%]
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  8%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [ 10%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [ 12%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 18%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 20%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 22%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 24%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 26%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 32%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 34%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 36%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 44%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 46%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 48%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 56%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 58%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 60%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 62%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 64%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 66%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 68%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 70%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 72%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 74%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 76%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 78%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 80%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 82%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 84%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 86%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [ 90%]
tests/test_store_agent_regressions.py::test_delete_all_chunks_preserves_explicit_parent_and_infers_suffix PASSED [ 92%]
tests/test_store_agent_regressions.py::test_metadata_isolated_from_caller_and_search_results PASSED [ 94%]
tests/test_store_agent_regressions.py::test_filter_before_top_k_and_no_filter_equivalence PASSED [ 96%]
tests/test_store_agent_regressions.py::test_empty_store_does_not_call_embedder_or_llm PASSED [ 98%]
tests/test_store_agent_regressions.py::test_agent_prompt_has_traceable_chunks_and_grounding PASSED [100%]

============================= 50 passed in 0.14s ==============================
```

**Số lượng bài test vượt qua (pass):** 50 / 50 bài test, trong đó có 3 test loader và 5 test hồi quy bổ sung. Kiểm thử đã chạy thành công trong môi trường Python 3.13.14.

Checkpoint 4: `python main.py "Chunking là gì?"` chạy thành công (exit code 0), nạp 5 tài liệu, search và gọi agent hoàn tất. Dòng `Skipping missing file: data/customer_support_playbook.txt` là bình thường vì file đó không có trong repo. Đây là kiểm tra luồng chạy, không phải đánh giá chất lượng trả lời của LLM thật.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                              | Câu B                                                                   | Dự đoán | Điểm thực tế | Đúng? |
| ---- | --------------------------------------------------- | ------------------------------------------------------------------------ | ---------- | ---------------- | ------- |
| 1    | "Học sinh đang chuẩn bị cho kỳ thi cuối kỳ." | "Students are preparing for the final exam."                             | cao        | cao              | Có     |
| 2    | "Một chiếc xe đang chạy trên đường."        | "Trời hôm nay rất nắng."                                             | thấp      | thấp            | Có     |
| 3    | "Tôi muốn tìm hiểu về chunking trong RAG."     | "Tôi đang nghiên cứu cách chia văn bản cho retrieval."            | cao        | cao              | Có     |
| 4    | "Chúng ta cần bảo mật dữ liệu."               | "Mặt trời mọc ở phía đông."                                       | thấp      | thấp            | Có     |
| 5    | "Vector database lưu trữ embedding."              | "Cơ sở dữ liệu vector lưu embedding cho tìm kiếm tương đồng." | cao        | cao              | Có     |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Điều bất ngờ nhất là hai câu có nghĩa tương tự nhưng dùng từ vựng hoàn toàn khác nhau vẫn có cosine similarity cao. Điều này cho thấy embedding không chỉ so khớp từ khóa mà còn biểu diễn ý nghĩa ở cấp độ semantic, phù hợp với text retrieval và RAG.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> Lưu ý quan trọng: benchmark này chạy trên `MockEmbedder` (MD5-based fallback), nên các score và top-3 là nhiễu ngữ nghĩa. Do đó, điểm thấp ở phần này không phản ánh code lỗi mà phản ánh backend không có khả năng biểu diễn ý nghĩa thật.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Q1 — Đăng ký học bổng HKĐ2026 | `student-financial-aid#0` và `undergraduate-scholarship#7` nhưng không chứa mốc 25/3/2026–08/4/2026 đúng với sinh viên | 0.2512 / 0.4167 | Không | Agent không thể trả lời đúng vì ngữ cảnh không chứa evidence chuẩn. |
| 2 | Q2 — Tín chỉ song ngành K50 | `student-support-page#3` và `undergraduate-scholarship#4` không chứa dữ liệu 14/15 tín chỉ cần thiết | 0.2771 / 0.2194 | Không | Không phản hồi đúng về ngưỡng tín chỉ của từng ngành. |
| 3 | Q3 — Học bổng VAS 2026 | `student-financial-aid#9`, `graduate-scholarship#3`, `undergraduate-scholarship-info#0` không chứa điều kiện 100% học phí + điểm 2,5 + 65 | 0.3671 / 0.3144 | Không | Không có một chunk đủ chi tiết để đáp ứng câu hỏi. |
| 4 | Q4 — Học bổng Toán học kỳ I 2026–2027 | `undergraduate-scholarship-info#0` và `undergraduate-scholarship-page#6` chỉ có dữ liệu tương tự nhưng không chứa mốc 09/09/2026 và số suất 150 | 0.2657 / 0.2441 | Không | Agent gặp lỗi vì thông tin quan trọng nằm ở doc đúng nhưng không có evidence đúng trong top-3. |
| 5 | Q5 — Học bổng HKC2026 K52 | `graduate-scholarship#7`, `student-support-page#0`, `undergraduate-scholarship#8` không chứa mốc đăng ký online 17/8–02/9 và nộp hồ sơ 04/9/07/9 | 0.2283 / 0.2790 | Không | Không trả lời đúng theo gold answer. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 0 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng benchmark với mock embedding có thể cho ra top-1 đúng tài liệu nhưng không chứa câu trả lời, và đây là sai lầm rất dễ mắc nếu chỉ chấm theo `doc_id` mà không kiểm evidence nội dung. Chúng tôi cũng thấy rõ rằng `metadata_filter` chỉ có ý nghĩa khi câu hỏi thật sự cần phân biệt đối tượng, chẳng hạn câu hỏi về sinh viên với staff hay K52. Khi backend không có ngữ nghĩa, mọi biến động score đều trở nên “nhiễu” và làm lẩn quẩn thông tin thực.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 0 / 10 |
| **Tổng phần cá nhân** | **50 / 60** |

> Cần lưu ý: điểm số thấp ở mục 5 phản ánh benchmark trên mock backend chứ không phải toàn bộ project lỗi. Tất cả phần code và test vẫn đạt 50/50 pass; sự suy giảm nằm ở chất lượng semantic retrieval trong môi trường mock.
