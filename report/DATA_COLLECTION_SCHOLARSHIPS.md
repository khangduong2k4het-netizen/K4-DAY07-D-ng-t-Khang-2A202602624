# Biên bản thu thập học bổng UEH

Ngày kiểm tra: **2026-09-19**. Corpus: `data/scholarships/` — **9 tài liệu, 8 URL nguồn, 8 tài liệu student và 1 tài liệu staff**. Kiểm kê trong `data/scholarships/sources.csv`; câu hỏi, đáp án và trích đoạn chứng cứ trong `report/scholarship_queries.json`.

## Truy cập và căn cứ nguồn

- Đã đọc [robots.txt của DSA UEH](https://dsa.ueh.edu.vn/robots.txt): `User-agent: *`, `Disallow: /wp-admin/`, `Allow: /wp-admin/admin-ajax.php`. Cả 8 URL bài thông báo nằm ngoài đường dẫn cấm.
- Tải trực tiếp bằng `Day7DataFoundationsCourse/1.0 (+educational-lab)`, chờ 1,1 giây giữa các lượt tải bài. Cả 8 trả HTTP 200, HTML với charset UTF-8 và có văn bản; không gặp body rỗng hoặc charset không hợp lệ.
- Không đăng nhập; không tải bảng ngân sách cần email sinh viên, danh sách cá nhân, hồ sơ minh chứng hoặc dữ liệu từ cổng `student.ueh.edu.vn`. Các địa chỉ cổng trong văn bản chỉ mô tả cách nộp hồ sơ.
- Footer nguồn ghi `© 2020 DSA - UEH. All Rights Reserved`. Không thấy điều khoản cấp phép mở trong các trang đã đọc. `public-source` theo quy ước lab chỉ nguồn thông báo công khai, **không phải giấy phép mở hay xác nhận đã được chủ sở hữu cấp phép tái phát hành**. Không gán CC-BY hoặc suy ra quyền sử dụng từ robots.txt.
- Các URL VinUni từng thử trả 403 đã được thay bằng UEH; corpus không có nội dung VinUni.

## Làm sạch và đối chiếu

Đã lấy vùng bài viết `bs-desc`, bỏ menu, phân loại tin, bài liên quan, footer, liên kết quảng cáo/cờ bạc, hình trang trí và thông tin liên hệ cá nhân. Đã đọc lại cả 9 file; giữ nội dung tiếng Việt, `language=vi`. `doc_id` và tiêu đề tiếng Anh theo yêu cầu người dùng. Một số ID chứa `graduate` hoặc `masters` là định danh do người dùng chọn, **không thể dùng để suy ra bậc học**; nội dung và tiêu đề quyết định phạm vi.

Đã phục hồi bảng thành Markdown, bổ sung tiêu đề mục, sửa danh sách bị dính dòng. Giữ yêu cầu dùng mẫu giấy tờ, bỏ lời dẫn giao diện trơ như “Xem tại đây”. Corpus không thay thế bộ mẫu hồ sơ trên trang gốc.

`masters-scholarship.md` cũ chứa nhầm bản VAS; đã thay bằng thông báo Hỗ trợ học tập K52. Kế hoạch chung được tách thành:

- `undergraduate-scholarship`: lịch và quy trình xử lý của đơn vị, `audience=staff`.
- `graduate-support-page`: phần sinh viên gửi đề nghị cộng điểm, `audience=student`.

Hai file cùng URL là chủ ý; phần việc sinh viên đã được bỏ khỏi file staff. CSV có 9 dòng, 8 URL duy nhất. Khi thu thập lại phải tách theo đối tượng và làm sạch; crawler mẫu chưa tự thực hiện hai bước này. Không chạy `--overwrite` trực tiếp lên bản đã làm sạch.

Các bản thô và manifest cũ trong `data/university/` đã chuyển ra khỏi corpus, lưu tạm tại `%TEMP%/ueh-raw-corpus-before-cleanup-20260919/` để khôi phục nếu cần. Hai tài liệu khởi động của lab vẫn ở `data/university/`, không thuộc benchmark học bổng.

## Giới hạn đã ghi nhận

| Tài liệu | Vấn đề nguồn | Cách xử lý |
| --- | --- | --- |
| undergraduate-scholarship | Kế hoạch ghi `31/9/2026`, khoảng `28/4/2026 – 18/5/2025`; lịch hành chính khác lịch thông báo sinh viên | Giữ nguyên, thêm `collection_note`; không dùng ngày mâu thuẫn làm gold answer |
| student-support-page | Thông báo HKĐ2026 nhưng đăng ký online ghi `22/4 – 15/5/2025)` | Không tự đổi năm; ghi chú, không đặt câu benchmark về mốc này |
| graduate-scholarship | Công thức điểm là ảnh, bảng ngân sách yêu cầu email sinh viên | Không thu thập phần này; không đặt câu về công thức/ngân sách |
| Tất cả | Chưa xác định phiên bản/ngày hiệu lực riêng của bài web | `document_version=not-stated`; không dùng ngày đăng hoặc số hiệu được dẫn chiếu làm phiên bản bài |

## Nạp dữ liệu và xác minh

```python
from pathlib import Path
from main import load_documents_from_files

docs = load_documents_from_files(
    [str(path) for path in sorted(Path("data/scholarships").glob("*.md"))]
)
student_docs = [doc for doc in docs if doc.metadata["audience"] == "student"]
```

`src/document_io.py` đọc frontmatter YAML phẳng với giá trị chuỗi của lab, không phải parser YAML tổng quát. Frontmatter không xuất hiện trong `Document.content`; ghi chú kiểm định nằm trong metadata. Các tiêu đề `##`/`###` dùng được để thử chunk theo mục.

```powershell
.venv/Scripts/python.exe scripts/validate_scholarship_corpus.py
.venv/Scripts/python.exe -m pytest tests/test_document_io.py -q
```

Kết quả: **9 tài liệu hợp lệ; manifest và CSV khớp; 5/5 câu có chứng cứ; lọc student giữ tài liệu đích và loại staff ở Q1; 3 kiểm thử loader đạt**. Máy hiện có Python 3.13.14; chưa xác minh bằng Python 3.11 chuẩn của lab. Pytest lần đầu lỗi quyền thư mục tạm mặc định; chạy lại với `PYTEST_DEBUG_TEMPROOT` trỏ tới thư mục tạm mới đã đạt.

Q1 phân biệt lịch hành chính `07/4/2026` với lịch đăng ký sinh viên `25/3/2026–08/4/2026`. Đây là chứng cứ về lọc audience, không phải kết quả đo top-k. Các phương thức `EmbeddingStore` hiện còn `NotImplementedError`, nên chưa chạy benchmark embedding hay tuyên bố điểm retrieval. Phần dữ liệu đã sẵn sàng cho bước đó.
