# U01-01 — Thiết lập môi trường AI Engineer

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 1 · **Giờ dự kiến:** 6 · **Độ khó:** Dễ
> **Tài liệu tham khảo:** MIT Missing Semester (6.NULL) L1-2 · Python Packaging User Guide · Real Python: Virtual Environments · [uv docs — Python versions](https://docs.astral.sh/uv/guides/install-python/)

---

## 1. Mục tiêu bài học

Sau bài này bạn phải:

1. Cài được Python 3.11+ và quản lý được **nhiều phiên bản Python** trên cùng 1 máy bằng `uv`.
2. Hiểu và dùng thành thạo **`uv`** để quản lý cả phiên bản Python lẫn dependency (thay cho pip/venv/pyenv/poetry rời rạc).
3. Biết phân biệt `pyproject.toml` vs `requirements.txt` vs lock file, và vì sao lock file bắt buộc phải có trong mọi dự án AI.
4. Cấu hình VS Code + các extension tối thiểu để làm việc hiệu quả.
5. Biết khi nào dùng Jupyter Notebook, khi nào dùng file `.py`, khi nào dùng Google Colab.
6. Tạo ra 1 repo mẫu (`ai-lab`) mà **người khác clone về chạy được ngay trong < 5 phút** — đây là kỹ năng nền tảng cho toàn bộ 52 tuần sau.

---

## 2. Lý thuyết

### 2.1. Vì sao không cài Python trực tiếp vào hệ điều hành

Hệ điều hành Linux/macOS thường có sẵn 1 bản Python dùng cho hệ thống (system Python). **Tuyệt đối không** cài package trực tiếp vào đó bằng `pip install` — dễ phá vỡ tool hệ thống. Ta cần:

- Một cách quản lý **nhiều phiên bản Python** (3.10, 3.11, 3.12...) song song.
- Một cách cô lập dependency **theo từng dự án** → dùng **virtual environment**.

Trước đây 2 việc này cần 2 công cụ riêng: `pyenv` (quản lý version) + `venv`/`poetry` (quản lý dependency). **Từ 2024, `uv` làm được cả hai trong 1 công cụ duy nhất** — đây là lý do lộ trình này không dùng `pyenv` nữa.

> **Sửa lại so với bản trước:** bài học này từng dạy dùng `pyenv` để quản lý phiên bản Python. Điều đó **không sai** nhưng **thừa** — vì `uv` (từ bản 0.3 trở lên) đã tích hợp sẵn khả năng tự tải và quản lý nhiều phiên bản Python (`uv python install`, `uv python pin`), không cần cài thêm `pyenv`. Giữ 2 công cụ chồng chéo chức năng chỉ gây rối: bạn phải nhớ `pyenv global` ảnh hưởng gì, `uv` có tôn trọng `.python-version` của pyenv hay không, PATH ai đứng trước ai... Quy tắc đơn giản nhất: **dùng 1 công cụ (`uv`) cho cả version lẫn dependency.**

### 2.2. `uv python` — quản lý phiên bản Python (thay cho pyenv)

```bash
# Liệt kê các phiên bản Python uv có thể cài (tự tải binary đã build sẵn, không cần biên dịch)
uv python list

# Cài 1 phiên bản Python cụ thể (uv tự tải về, không phụ thuộc Python đã có trên máy)
uv python install 3.11

# Đặt phiên bản Python cho riêng dự án hiện tại (tạo file .python-version)
cd my-project
uv python pin 3.11

# Chạy trực tiếp bằng 1 phiên bản Python cụ thể mà không cần cài global
uv run --python 3.12 python --version
```

Cơ chế: khi bạn chạy `uv run` hoặc `uv sync` trong 1 thư mục, `uv` đọc file `.python-version` (nếu có) hoặc trường `requires-python` trong `pyproject.toml`, rồi **tự tải đúng bản Python đó** (nếu chưa có trên máy) và dùng nó để tạo venv — hoàn toàn không cần bạn tự quản lý PATH hay shim như `pyenv`.

**Vậy khi nào vẫn cần biết đến `pyenv`?** Nếu bạn tham gia 1 dự án/công ty đã dùng sẵn `pyenv` từ trước (rất phổ biến trong các codebase cũ trước 2024), bạn cần biết đọc file `.python-version` do `pyenv` tạo ra và lệnh `pyenv install/global/local` để không bỡ ngỡ — nhưng **không cần tự cài mới** cho dự án của riêng bạn trong lộ trình này.

### 2.3. venv vs conda vs uv — chọn cái nào?

| Công cụ | Quản lý Python version? | Quản lý package | Tốc độ resolve | Khi nào dùng |
|---|---|---|---|---|
| `venv` (built-in) | Không | pip | Chậm | Dự án đơn giản, không muốn cài thêm gì |
| `pyenv` | Có (chỉ version, không quản lý package) | — | — | Codebase cũ đã dùng sẵn; không cần cho dự án mới |
| `conda`/`mamba` | Có | conda packages + pip | Trung bình (mamba nhanh) | Cần binary phức tạp (CUDA, MKL) khó build bằng pip |
| `poetry` | Không (thường kết hợp pyenv) | pip-compatible | Chậm | Dự án Python thuần, cần publish package |
| **`uv`** | **Có (tự tải, tích hợp sẵn)** | pip-compatible, viết bằng Rust | **Rất nhanh (10-100x pip)** | **Mặc định cho mọi dự án trong lộ trình này** |

**Quyết định của lộ trình: dùng `uv` làm công cụ duy nhất, cho cả version lẫn dependency.** Lý do: `uv` giải quyết dependency graph bằng Rust nên nhanh hơn pip 10-100 lần, và tích hợp sẵn: tải Python version → tạo venv → resolve dependency → lock file, tất cả trong 1 binary, không cần cài thêm `pyenv`/`poetry` chồng chéo lên nhau.

**Ngoại lệ duy nhất đáng cân nhắc `conda`**: khi bạn cần 1 package có phần biên dịch native phức tạp mà không có sẵn "wheel" cho hệ điều hành/kiến trúc CPU của bạn (một số thư viện khoa học cũ, hoặc bản CUDA toolkit đặc thù) — khi đó `conda`/`mamba` có kho binary riêng dễ cài hơn. Với các thư viện AI phổ biến hiện nay (numpy, pandas, torch, transformers...) thì `uv` xử lý tốt vì hầu hết đã publish wheel sẵn trên PyPI.

```bash
# Cài uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Khởi tạo 1 dự án mới
uv init ai-lab && cd ai-lab

# Thêm dependency (tự tạo venv + cài + ghi vào pyproject.toml + lock file)
uv add numpy pandas matplotlib

# Chạy script trong venv của dự án mà không cần "activate" thủ công
uv run python check_env.py

# Đồng bộ lại venv từ lock file (dùng khi clone repo về máy khác)
uv sync
```

### 2.4. pyproject.toml vs requirements.txt vs lock file

- **`pyproject.toml`**: khai báo *ý định* — "dự án này cần numpy >= 1.26". Đây là phần **con người đọc và sửa**.
- **`requirements.txt`** (cách cũ): thường bị lẫn lộn giữa khai báo ý định và khai báo phiên bản chính xác — đây là nguồn gốc của rất nhiều lỗi "chạy trên máy tôi nhưng không chạy trên máy bạn".
- **Lock file** (`uv.lock`): khoá **chính xác từng phiên bản của từng package, kể cả transitive dependency** (package mà package bạn cài phụ thuộc vào), kèm hash để kiểm tra toàn vẹn. Đây là phần **máy đọc, không nên sửa tay**.

> **Nguyên tắc:** `pyproject.toml` trả lời "tôi cần gì", lock file trả lời "chính xác cài cái gì". Luôn commit cả 2 vào git. Không commit `.venv/`.

### 2.5. Semantic Versioning (SemVer)

Phiên bản dạng `MAJOR.MINOR.PATCH` (ví dụ `2.1.4`):
- **MAJOR** tăng khi có breaking change (code cũ có thể hỏng).
- **MINOR** tăng khi thêm tính năng nhưng tương thích ngược.
- **PATCH** tăng khi chỉ sửa lỗi.

Khai báo `numpy>=1.26,<2.0` nghĩa là "chấp nhận mọi bản vá và tính năng mới của nhánh 1.26 trở lên, nhưng không tự động nhảy sang major version 2 vì có thể breaking".

### 2.6. VS Code cho AI Engineer

Extension tối thiểu cần cài:
1. **Python** (Microsoft) — chạy/debug code Python.
2. **Pylance** — type checking, autocomplete thông minh (dựa trên Pyright).
3. **Jupyter** — chạy notebook `.ipynb` ngay trong VS Code.
4. **Ruff** — linter + formatter cực nhanh (thay thế flake8 + black + isort).

Phím tắt quan trọng:
- `F5`: chạy debug
- `Ctrl+Shift+P` → "Python: Select Interpreter": chọn đúng venv của dự án (rất hay quên bước này!)
- `Shift+Enter` trong notebook: chạy 1 cell

### 2.7. Jupyter Notebook vs script `.py` vs Colab

| Công cụ | Ưu điểm | Nhược điểm | Dùng khi nào |
|---|---|---|---|
| Jupyter Notebook | Chạy từng cell, xem kết quả ngay, vẽ biểu đồ inline | Khó version control (diff file `.ipynb` rất rối), dễ chạy sai thứ tự cell | EDA, thử nghiệm nhanh, trình bày kết quả |
| Script `.py` | Version control sạch, test được, chạy production | Không xem kết quả từng bước trực quan | Code sẽ chạy lại nhiều lần, pipeline, thư viện dùng chung |
| Google Colab | Miễn phí GPU, không cần cài gì, chia sẻ dễ | Mất session sau ~12h, mất dữ liệu nếu không mount Drive, giới hạn tài nguyên | Thử nghiệm cần GPU miễn phí, học tập, demo nhanh |

**Nguyên tắc của lộ trình này**: logic quan trọng (được tái sử dụng) luôn nằm trong file `.py` trong package; notebook chỉ dùng để *gọi* logic đó và trực quan hoá — không viết logic cốt lõi trực tiếp trong notebook. Đây chính là nội dung Bài 1.14 sẽ đào sâu hơn.

### 2.8. Google Colab — những điều cần biết

```python
# Mount Google Drive để giữ dữ liệu qua các phiên
from google.colab import drive
drive.mount('/content/drive')

# Kiểm tra GPU được cấp
!nvidia-smi

# Cài thêm package (mỗi phiên phải cài lại vì máy ảo bị huỷ)
!pip install -q package_name
```

**Cạm bẫy Colab**: máy ảo bị **thu hồi sau ~12 giờ** (hoặc ít hơn với tài khoản free khi ít hoạt động) — mọi thứ ngoài `/content/drive` sẽ mất, kể cả package đã cài. Luôn lưu checkpoint/kết quả quan trọng vào Drive.

---

## 3. Bài tập thực hành

### BT1 — Tạo môi trường tái lập được bằng lock file

**Yêu cầu:**
1. Dùng `uv` tạo 1 dự án mới tên `ai-lab`.
2. Thêm các dependency: `numpy`, `pandas`, `matplotlib`.
3. Xuất ra được lock file.
4. **Xoá hoàn toàn** thư mục `.venv`.
5. Chạy `uv sync` để tái tạo lại venv **chỉ từ lock file**.
6. Chứng minh: viết 1 script in ra phiên bản chính xác của numpy, so sánh trước và sau khi tái tạo — phải giống hệt nhau.

### BT2 — Script kiểm tra môi trường

Viết file `check_env.py` in ra:
- Phiên bản Python đang chạy
- Phiên bản của numpy, pandas, matplotlib, torch (nếu có)
- Có GPU khả dụng hay không (dùng `torch.cuda.is_available()`)
- Hệ điều hành đang chạy

### Tiêu chí hoàn thành (DoD)

- [ ] Repo `ai-lab` có `pyproject.toml`, `uv.lock`, `.gitignore`, `README.md`.
- [ ] Người khác (hoặc chính bạn trên 1 thư mục sạch khác) chỉ cần `git clone` + `uv sync` + `uv run python check_env.py` là chạy được, **không cần sửa gì thêm**, trong dưới 5 phút.
- [ ] `.venv/` **không** nằm trong git (kiểm tra bằng `git status` sau khi tạo venv).
- [ ] 1 notebook `00_hello.ipynb` chạy được cả ở local (qua VS Code/Jupyter) lẫn khi upload lên Colab.

---

## 4. Lời giải chi tiết

> Đọc phần này **sau khi đã tự làm** BT1 và BT2. Nếu bạn thấy lời giải khác cách bạn làm nhưng cùng đạt DoD — vẫn tính là đạt, đây không phải đáp án duy nhất.

### 4.1. Lời giải BT1 — Môi trường tái lập được

**Bước 1 — Cài `uv` (nếu chưa có):**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Kiểm tra
uv --version
```

**Bước 2 — Cài Python 3.11 qua `uv` (không cần pyenv):**

```bash
uv python install 3.11
uv python list   # xác nhận 3.11 đã có trong danh sách
```

**Bước 3 — Khởi tạo dự án và ghim đúng phiên bản Python:**

```bash
uv init ai-lab
cd ai-lab
uv python pin 3.11   # tạo file .python-version = 3.11
```

Lệnh này tạo ra cấu trúc:

```
ai-lab/
├── .gitignore
├── .python-version
├── README.md
├── main.py
└── pyproject.toml
```

**Bước 4 — Thêm dependency:**

```bash
uv add numpy pandas matplotlib
```

Sau lệnh này, `uv` sẽ:
1. Tạo `.venv/` trong thư mục dự án (nếu chưa có).
2. Giải (resolve) toàn bộ dependency graph.
3. Cài đặt vào `.venv/`.
4. Cập nhật `pyproject.toml`:

```toml
[project]
name = "ai-lab"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "matplotlib>=3.9.0",
    "numpy>=2.0.0",
    "pandas>=2.2.0",
]
```

5. Tạo/cập nhật `uv.lock` — file này **dài hàng trăm dòng**, khoá chính xác từng version + hash của numpy, pandas, matplotlib **và mọi thư viện mà chúng phụ thuộc vào** (ví dụ pandas phụ thuộc `python-dateutil`, `pytz`...).

**Bước 5 — Ghi lại phiên bản numpy hiện tại (để đối chiếu sau):**

```bash
uv run python -c "import numpy; print(numpy.__version__)"
# Ví dụ output: 2.1.3
```

**Bước 6 — Xoá venv và tái tạo:**

```bash
rm -rf .venv
uv sync
```

`uv sync` đọc **lock file** (không đọc lại `pyproject.toml` để giải dependency từ đầu) → tạo `.venv` mới → cài **chính xác** các phiên bản đã khoá.

**Bước 7 — Kiểm chứng:**

```bash
uv run python -c "import numpy; print(numpy.__version__)"
# Phải in ra: 2.1.3 (giống hệt bước 4)
```

Nếu 2 số này khác nhau → có gì đó sai (ví dụ bạn quên commit lock file, hoặc dùng nhầm `uv add` thay vì `uv sync` khiến nó giải lại dependency).

**Bước 8 — Đảm bảo `.venv` không vào git:**

Kiểm tra file `.gitignore` (được `uv init` tự tạo sẵn) phải có dòng:

```gitignore
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
```

```bash
git init
git add .
git status   # .venv/ KHÔNG được xuất hiện trong danh sách staged
```

### 4.2. Lời giải BT2 — Script kiểm tra môi trường

Tạo file `check_env.py`:

```python
"""Script kiểm tra môi trường phát triển AI Engineer.

Chạy bằng: uv run python check_env.py
"""
import platform
import sys


def check_package(name: str) -> str:
    """Trả về phiên bản của package, hoặc 'không cài' nếu chưa cài đặt."""
    try:
        module = __import__(name)
        version = getattr(module, "__version__", "không rõ phiên bản")
        return version
    except ImportError:
        return "không cài"


def check_gpu() -> str:
    """Kiểm tra GPU khả dụng thông qua PyTorch, nếu PyTorch đã được cài."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_count = torch.cuda.device_count()
            return f"Có ({gpu_count} GPU, ví dụ: {gpu_name})"
        return "Không (torch đã cài nhưng không thấy CUDA)"
    except ImportError:
        return "Không kiểm tra được (chưa cài torch)"


def main() -> None:
    print("=" * 50)
    print("KIỂM TRA MÔI TRƯỜNG AI ENGINEER")
    print("=" * 50)

    print(f"\n[Hệ thống]")
    print(f"  Hệ điều hành : {platform.system()} {platform.release()}")
    print(f"  Kiến trúc CPU: {platform.machine()}")
    print(f"  Python       : {sys.version.split()[0]}")
    print(f"  Python path  : {sys.executable}")

    print(f"\n[Thư viện chính]")
    for pkg in ("numpy", "pandas", "matplotlib", "torch"):
        print(f"  {pkg:<12}: {check_package(pkg)}")

    print(f"\n[GPU]")
    print(f"  CUDA khả dụng: {check_gpu()}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
```

**Chạy thử:**

```bash
uv run python check_env.py
```

**Output mẫu (không có torch/GPU):**

```
==================================================
KIỂM TRA MÔI TRƯỜNG AI ENGINEER
==================================================

[Hệ thống]
  Hệ điều hành : Linux 6.8.0
  Kiến trúc CPU: x86_64
  Python       : 3.11.9
  Python path  : /home/user/ai-lab/.venv/bin/python

[Thư viện chính]
  numpy       : 2.1.3
  pandas      : 2.2.3
  matplotlib  : 3.9.2
  torch       : không cài

[GPU]
  CUDA khả dụng: Không kiểm tra được (chưa cài torch)

==================================================
```

**Giải thích các quyết định thiết kế trong code:**
- Dùng `try/except ImportError` thay vì kiểm tra package có trong `pip list` — vì cách này đúng với triết lý "thử làm, bắt lỗi nếu thất bại" (EAFP — *Easier to Ask Forgiveness than Permission*) rất Pythonic, sẽ học kỹ ở Bài 1.6.
- Tách `check_package` và `check_gpu` thành hàm riêng, có docstring, có type hint (`-> str`) — đúng chuẩn sẽ học ở Bài 1.5.
- `if __name__ == "__main__":` đảm bảo file này vừa chạy được trực tiếp, vừa import được vào chỗ khác mà không tự động chạy `main()` — sẽ học kỹ ở Bài 1.3.

### 4.3. README.md mẫu cho repo `ai-lab`

```markdown
# ai-lab

Repo thực hành cá nhân cho lộ trình AI Engineer — Unit 01.

## Yêu cầu

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) đã cài đặt

## Cài đặt

\`\`\`bash
git clone <your-repo-url>
cd ai-lab
uv sync
\`\`\`

## Chạy thử

\`\`\`bash
uv run python check_env.py
\`\`\`

## Cấu trúc

- `check_env.py` — script kiểm tra môi trường (Python, package, GPU)
- `00_hello.ipynb` — notebook thử nghiệm đầu tiên, chạy được cả local và Colab
```

### 4.4. Đáp án 5 câu tự kiểm tra kiến thức

**Câu 1: Khác nhau venv vs conda?**

> `venv` chỉ cô lập package Python thuần (dựa trên `pip`), dùng chung phiên bản Python đã cài trên máy. `conda` là trình quản lý gói **đa ngôn ngữ** (Python, C, R...) và **có thể tự cài cả phiên bản Python khác** vào environment — hữu ích khi cần các thư viện có phần biên dịch C/CUDA phức tạp mà pip khó build (ví dụ một số bản CUDA toolkit cũ). Với dự án Python thuần và pip-compatible, `uv`/`venv` gọn nhẹ và nhanh hơn.

**Câu 2: Vì sao cần lock file?**

> `pyproject.toml` chỉ khai báo khoảng version chấp nhận được (ví dụ `numpy>=1.26`). Nếu 2 người cùng chạy `pip install` vào 2 thời điểm khác nhau, họ có thể nhận **2 phiên bản numpy khác nhau** (vì numpy ra bản mới liên tục) → "chạy trên máy tôi nhưng lỗi trên máy bạn". Lock file khoá **chính xác từng phiên bản, của cả transitive dependency**, đảm bảo mọi người luôn cài đúng 1 bộ gói giống hệt nhau.

**Câu 3: `__pycache__` có nên commit?**

> Không. Đây là thư mục Python tự sinh ra chứa file `.pyc` (bytecode đã biên dịch) để tăng tốc lần chạy sau — hoàn toàn là artifact tạm thời, tái tạo tự động, phụ thuộc vào phiên bản Python đang chạy. Commit nó vào git chỉ gây rác và xung đột không cần thiết. Luôn có `__pycache__/` trong `.gitignore`.

**Câu 4: `PYTHONPATH` dùng làm gì?**

> `PYTHONPATH` là biến môi trường liệt kê thêm các thư mục mà Python sẽ tìm khi bạn `import` một module, bổ sung vào danh sách mặc định (thư mục hiện tại, thư mục cài package, thư viện chuẩn). Hữu ích khi bạn muốn import code từ một thư mục không nằm trong cấu trúc package chuẩn mà không muốn cài đặt (`pip install -e .`) nó. Trong dự án có cấu trúc `pyproject.toml` chuẩn, ta thường ưu tiên cài package ở chế độ "editable" (`uv pip install -e .`) thay vì chỉnh `PYTHONPATH` thủ công, để tránh phụ thuộc vào biến môi trường dễ quên.

**Câu 5: Colab mất dữ liệu khi nào?**

> Colab chạy trên 1 máy ảo tạm thời. Dữ liệu **mất** khi: (a) máy ảo bị thu hồi sau khoảng ~12 giờ hoạt động liên tục hoặc ~90 phút không tương tác (với free tier), (b) bạn chủ động "Disconnect and delete runtime", hoặc (c) hết phiên do quá tải hệ thống của Google. Mọi thứ lưu ở `/content/` (không phải `/content/drive/`) sẽ mất hoàn toàn, bao gồm cả package đã `pip install` (phải cài lại mỗi phiên) và file bạn tạo ra. Giải pháp: luôn `drive.mount()` và lưu checkpoint/kết quả quan trọng vào `/content/drive/MyDrive/...`.

---

## 5. Tổng kết & bước tiếp theo

Bạn đã có:
- ✅ Một cách quản lý Python version và dependency chuyên nghiệp, nhanh, tái lập được — tất cả chỉ bằng `uv`.
- ✅ Repo mẫu `ai-lab` — **hãy giữ và mở rộng repo này**, nó sẽ là nền cho các bài tập tiếp theo của Unit 01.
- ✅ Hiểu rõ khi nào dùng notebook, khi nào dùng script, khi nào dùng Colab.

**Bài tiếp theo:** U01-02 — Python core: kiểu dữ liệu & luồng điều khiển.

---

## 6. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| Repo có đủ `pyproject.toml` + `uv.lock` + `.gitignore` + `README.md` | 2 |
| `uv sync` tái tạo môi trường thành công, version khớp trước/sau | 3 |
| `check_env.py` chạy đúng, in đủ thông tin yêu cầu, có type hint + docstring | 3 |
| Trả lời đúng ≥4/5 câu hỏi tự kiểm tra (viết ra, không chỉ nghĩ trong đầu) | 2 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel, ghi ngày hoàn thành và giờ thực tế. Dưới 8 → xem lại phần nào sai trong lời giải chi tiết, sửa và nộp lại.
