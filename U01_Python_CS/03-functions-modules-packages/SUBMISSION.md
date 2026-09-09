# Bài nộp — U01-03 Hàm, Module, Package và Cấu trúc Import

## Ngày bắt đầu / hoàn thành

- Bắt đầu:
- Hoàn thành:
- Số giờ thực tế đã bỏ ra:

## Phần 2.1 — `mytools/stats.py`: tham số hàm

- Output `compute_stats(values, precision=2)`:
- Output lỗi khi gọi `compute_stats(values, 2)` (không dùng tên):

## Phần 2.2 — `mytools/stats.py`: closure đếm lượt gọi

- Output `get_stats_call_count()`:

## Phần 2.3 — `mytools/fib.py`

- Output `benchmark(n)`:
- Output `@timeit` giữ đúng `__name__`:

## Phần 2.4 — Đóng gói package

- Xác nhận `pip install -e .` thành công:
- Output `from mytools import compute_stats` chạy từ thư mục khác:

## Phần 2.5 — Diễn tập circular import

- Output lỗi `ImportError` thật:
- Giải thích hướng phụ thuộc đúng nên sửa thế nào:

## Phần 2.6 — Hoàn thiện `mytools/cli.py`

- Output `mytools stats --file ... --col ... --precision 2`:

```
(dán output ở đây)
```

- Output `mytools fib-benchmark --n 30`:

```
(dán output ở đây)
```

- Output `python -m mytools stats --help`:

## Trả lời quiz (3 câu)

**Câu 1: LEGB tra cứu theo thứ tự nào?**

**Câu 2: `lru_cache` lưu gì và rủi ro bộ nhớ là gì?**

**Câu 3: Vì sao relative import lỗi khi chạy trực tiếp file?**

## Tự đánh giá

- Mức độ tự tin (1-5):
- Điều còn chưa rõ:
