# Bài nộp — U01-04 OOP và Thiết kế Lớp trong Python

## Ngày bắt đầu / hoàn thành

- Bắt đầu:
- Hoàn thành:
- Số giờ thực tế đã bỏ ra:

## Phần 2.1 — `ai_lab/models/base.py`: `@property is_fitted`

- Output kiểm tra `is_fitted` không có setter:

## Phần 2.2 — `DummyModel`, `LinearModel`, `Trainer` (composition)

- Output `Trainer(DummyModel())` và `Trainer(LinearModel())`:

## Phần 2.3 — `CSVDataset` (magic methods)

- Output `repr(dataset)`, `len(dataset)`, `dataset[0]`:

## Phần 2.4 — `TrainConfig`

- Output validate `precision`:
- Xác nhận `tags` độc lập giữa các instance:

## Phần 2.5 — `BaseModel` (ABC) + `Dataset` (Protocol)

- Output `isinstance(csv_dataset, Dataset)` (phải `True` dù không kế thừa):
- Output `TypeError` khi thiếu implement `predict`:

## Phần 2.6 — `ModelType` + `create_model_from_name`

- Output với model hợp lệ và không hợp lệ:

## Phần 2.7 — Lệnh `ai-lab train`

- Output `ai-lab train --model linear`:

```
(dán output ở đây)
```

- Output `ai-lab train --model dummy`:

```
(dán output ở đây)
```

- Xác nhận `run_pipeline`/`Trainer` không sửa dòng nào khi đổi `--model` (Có/Không):

## Trả lời quiz (3 câu)

**Câu 1: Khác nhau ABC vs Protocol?**

**Câu 2: Khi nào dùng dataclass thay class thường?**

**Câu 3: `__eq__` mà không có `__hash__` gây lỗi gì?**

## Tự đánh giá

- Mức độ tự tin (1-5):
- Điều còn chưa rõ:
