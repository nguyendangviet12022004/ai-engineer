# Bài nộp — U01-05 Type Hints, Pydantic v2 và Cấu hình

## Ngày bắt đầu / hoàn thành

- Bắt đầu:
- Hoàn thành:
- Số giờ thực tế đã bỏ ra:

## Phần 2.1 — Typing cơ bản

- Output `find_user`, `select_model`, `process_record`, `Box`, `apply_twice`:

## Phần 2.2 — `mypy --strict`

- Output `mypy --strict schemas.py` (code đúng):
- Output `mypy --strict schemas_buggy.py` (3 lỗi cố ý):

## Phần 2.3 — 4 model Pydantic

- Output `TrainRequest.model_dump()`/`model_dump_json()`:
- Output lỗi `TrainConfig` khi tổng tỉ lệ ≠ 1.0:
- Output lỗi `EvalResult` khi `accuracy` ngoài khoảng:

## Phần 2.4 — `AppSettings`

- Output đọc từ `.env`:
- Output khi override bằng biến môi trường (`MAX_EPOCHS=999`):
- Output `mypy --strict config.py` trước và sau khi thêm `# type: ignore[call-arg]`:

## Phần 2.5 — `parse_train_request`

- Output cả 4 trường hợp (JSON sai cú pháp, sai kiểu, sai Literal, hợp lệ):

## Phần 2.6 — `demo.py`

- Output `python demo.py`:

```
(dán output ở đây)
```

- Output `mypy --strict schemas.py config.py demo.py`:

```
(dán output ở đây)
```

- Thử đổi `epochs` thành 60 trong `demo.py`, dán output "Rejected":

## Trả lời quiz (3 câu)

**Câu 1: Khác nhau `Optional[X]` và `X | None`?**

**Câu 2: Pydantic v1 vs v2 khác gì?**

**Câu 3: `BaseSettings` ưu tiên `.env` hay biến môi trường?**

## Tự đánh giá

- Mức độ tự tin (1-5):
- Điều còn chưa rõ:
