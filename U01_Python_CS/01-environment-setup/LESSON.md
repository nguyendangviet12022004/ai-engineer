# U01-01 — Thiết lập môi trường AI Engineer

> **Unit:** U01 — Python & Nền tảng CS cho AI Engineer
> **Tuần:** 1 · **Giờ dự kiến:** 6 · **Độ khó:** Dễ
> **Tài liệu tham khảo:** MIT Missing Semester (6.NULL) L1-2 · Python Packaging User Guide · Real Python: Virtual Environments · [uv docs — Python versions](https://docs.astral.sh/uv/guides/install-python/)
> **Quy ước bắt buộc:** Toàn bộ code, comment, docstring, tên biến/hàm trong bài này **100% tiếng Anh**. Phần giải thích lý thuyết bằng tiếng Việt.
> **Cách dùng file này:** Đọc lý thuyết từng phần → làm ngay bài tập của phần đó (tick ☐ → ☑) → cuối bài có 1 dự án tổng hợp dùng lại mọi thứ đã làm.

---

## 1. Mục tiêu bài học

Sau bài này bạn phải:

- [ ] Cài được Python 3.11+ và quản lý được nhiều phiên bản Python bằng `uv` (không cần `pyenv`).
- [ ] Dùng thành thạo `uv` để quản lý dependency, phân biệt `pyproject.toml` vs lock file.
- [ ] Cấu hình VS Code + extension tối thiểu.
- [ ] Biết khi nào dùng Jupyter Notebook, khi nào dùng script `.py`, khi nào dùng Colab.
- [ ] Tạo ra 1 repo mẫu (`ai-lab`) mà người khác clone về chạy được ngay trong < 5 phút.

---

## 2. Phần 2.1 — `uv`: quản lý Python version và dependency

### Lý thuyết

Hệ điều hành Linux/macOS thường có sẵn 1 bản Python cho hệ thống (system Python). **Tuyệt đối không** cài package trực tiếp vào đó — dễ phá vỡ tool hệ thống.

Trước đây cần 2 công cụ riêng: `pyenv` (quản lý version) + `venv`/`poetry` (quản lý dependency). **Từ 2024, `uv` làm được cả hai trong 1 công cụ duy nhất** — đây là lý do lộ trình này không dùng `pyenv`.

```bash
# Cài uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version

# Cài 1 phiên bản Python cụ thể (uv tự tải, không cần Python có sẵn trên máy)
uv python install 3.11
uv python list

# Khởi tạo dự án + ghim phiên bản Python
uv init ai-lab && cd ai-lab
uv python pin 3.11        # tạo file .python-version

# Thêm dependency (tự tạo venv + cài + ghi vào pyproject.toml + lock file)
uv add numpy pandas matplotlib

# Chạy script trong venv của dự án mà không cần "activate" thủ công
uv run python check_env.py

# Đồng bộ lại venv từ lock file (dùng khi clone repo về máy khác)
uv sync
```

**`pyproject.toml` vs lock file:** `pyproject.toml` khai báo *ý định* ("cần numpy >= 1.26") — con người đọc/sửa. Lock file (`uv.lock`) khoá **chính xác từng phiên bản, kể cả transitive dependency**, kèm hash — máy đọc, không sửa tay. Luôn commit cả 2, không commit `.venv/`.

**Bảng so sánh nhanh:**

| Công cụ | Quản lý version? | Quản lý package | Tốc độ | Dùng khi nào |
|---|---|---|---|---|
| `venv` (built-in) | Không | pip | Chậm | Dự án đơn giản |
| `pyenv` | Có (chỉ version) | — | — | Codebase cũ đã dùng sẵn |
| `conda`/`mamba` | Có | conda + pip | Trung bình | Cần binary CUDA/MKL phức tạp |
| **`uv`** | **Có (tự tải)** | pip-compatible, Rust | **Rất nhanh (10-100x pip)** | **Mặc định trong lộ trình này** |

### Bài tập 2.1 — Môi trường tái lập được

- [ ] **BT 2.1.1** — Dùng `uv` tạo dự án `ai-lab`, cài Python 3.11 qua `uv python install`, ghim version bằng `uv python pin`.
- [ ] **BT 2.1.2** — Thêm dependency `numpy`, `pandas`, `matplotlib` bằng `uv add`. Ghi lại phiên bản numpy hiện tại.
- [ ] **BT 2.1.3** — Xoá hoàn toàn `.venv/`, chạy `uv sync` để tái tạo. Kiểm chứng phiên bản numpy sau khi tái tạo **giống hệt** trước đó.
- [ ] **BT 2.1.4** — Kiểm tra `.gitignore` có `.venv/` — chạy `git status` sau khi tạo venv, xác nhận `.venv/` không xuất hiện trong danh sách staged.

<details>
<summary><strong>Lời giải chi tiết BT 2.1</strong> (bấm để mở)</summary>

```bash
uv python install 3.11
uv python list

uv init ai-lab
cd ai-lab
uv python pin 3.11

uv add numpy pandas matplotlib
uv run python -c "import numpy; print(numpy.__version__)"
# Ví dụ output: 2.1.3   <- ghi lại số này

rm -rf .venv
uv sync

uv run python -c "import numpy; print(numpy.__version__)"
# Phải in ra: 2.1.3 (giống hệt trước đó)
```

Kiểm tra `.gitignore` (được `uv init` tự tạo sẵn) phải có:
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

Nếu 2 số phiên bản numpy khác nhau → có gì đó sai (quên commit lock file, hoặc dùng nhầm `uv add` thay vì `uv sync`).
</details>

---

## 3. Phần 2.2 — VS Code cho AI Engineer

### Lý thuyết

Extension tối thiểu:
1. **Python** (Microsoft) — chạy/debug code.
2. **Pylance** — type checking, autocomplete (dựa trên Pyright).
3. **Jupyter** — chạy notebook `.ipynb` ngay trong VS Code.
4. **Ruff** — linter + formatter cực nhanh (thay flake8 + black + isort).

Phím tắt quan trọng: `F5` chạy debug · `Ctrl+Shift+P` → "Python: Select Interpreter" (rất hay quên bước này!) · `Shift+Enter` chạy 1 cell trong notebook.

### Bài tập 2.2 — Cấu hình VS Code

- [ ] **BT 2.2.1** — Cài đủ 4 extension trên.
- [ ] **BT 2.2.2** — Mở thư mục `ai-lab`, dùng "Python: Select Interpreter" chọn đúng `.venv` của dự án (không phải Python hệ thống). Chụp ảnh màn hình thanh trạng thái góc dưới bên trái xác nhận đúng interpreter.
- [ ] **BT 2.2.3** — Đặt 1 breakpoint trong `check_env.py` (sẽ viết ở Phần 2.4), chạy `F5`, xác nhận debugger dừng đúng chỗ.

<details>
<summary><strong>Lời giải chi tiết BT 2.2</strong></summary>

Không có code — đây là bài tập thao tác UI. Tiêu chí xác nhận: thanh trạng thái VS Code (góc dưới trái) hiển thị đường dẫn `.venv/bin/python` của đúng dự án `ai-lab`, không phải `/usr/bin/python3` hay bất kỳ Python hệ thống nào khác.
</details>

---

## 4. Phần 2.3 — Notebook vs Script vs Colab

### Lý thuyết

| Công cụ | Ưu điểm | Nhược điểm | Dùng khi nào |
|---|---|---|---|
| Jupyter Notebook | Chạy từng cell, xem kết quả ngay | Khó version control, dễ chạy sai thứ tự cell | EDA, thử nghiệm nhanh |
| Script `.py` | Version control sạch, test được | Không xem kết quả từng bước | Logic tái sử dụng, pipeline |
| Google Colab | Miễn phí GPU, chia sẻ dễ | Mất session ~12h, mất dữ liệu nếu không mount Drive | Cần GPU miễn phí, demo |

**Nguyên tắc của lộ trình:** logic quan trọng nằm trong file `.py`; notebook chỉ *gọi* logic đó và trực quan hoá.

```python
# Colab: mount Drive để giữ dữ liệu qua các phiên
from google.colab import drive
drive.mount('/content/drive')
!nvidia-smi
```

**Cạm bẫy Colab:** máy ảo bị thu hồi sau ~12 giờ (hoặc sớm hơn nếu ít hoạt động) — mọi thứ ngoài `/content/drive` sẽ mất, kể cả package đã cài.

### Bài tập 2.3 — Notebook chạy được cả 2 nơi

- [ ] **BT 2.3.1** — Tạo `00_hello.ipynb` trong `ai-lab`, import numpy/pandas, vẽ 1 biểu đồ đơn giản bằng matplotlib.
- [ ] **BT 2.3.2** — Chạy notebook này thành công trong VS Code (dùng kernel từ `.venv`).
- [ ] **BT 2.3.3** — Upload notebook lên Google Colab, mount Drive, chạy lại thành công (phải `!pip install` lại các package vì Colab không dùng `.venv` của bạn).

<details>
<summary><strong>Lời giải chi tiết BT 2.3</strong></summary>

```python
# 00_hello.ipynb — cell 1
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# cell 2
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title("Hello, AI Engineer roadmap")
plt.xlabel("x")
plt.ylabel("sin(x)")
plt.show()

# cell 3 — chỉ chạy trên Colab, bỏ qua khi chạy local
# from google.colab import drive
# drive.mount('/content/drive')
```

Trên Colab, thêm 1 cell đầu tiên: `!pip install -q numpy pandas matplotlib` (Colab không đọc `pyproject.toml`/`uv.lock` của bạn, nó có môi trường Python riêng).
</details>

---

## 5. Dự án tổng hợp — Repo `ai-lab` hoàn chỉnh

Dùng lại **toàn bộ** những gì đã làm ở Phần 2.1-2.3 để hoàn thiện 1 repo chuẩn, sẵn sàng dùng cho mọi bài học tiếp theo của Unit 01.

### Yêu cầu

- [ ] **DA.1** — Viết `check_env.py`: in ra phiên bản Python, phiên bản numpy/pandas/matplotlib/torch (nếu có), có GPU hay không, hệ điều hành. Có type hint + docstring đầy đủ (100% tiếng Anh).
- [ ] **DA.2** — Viết `README.md` mô tả cách cài đặt và chạy, chỉ dùng lệnh `uv sync` + `uv run`.
- [ ] **DA.3** — Đặt breakpoint trong `check_env.py`, debug bằng `F5` trong VS Code đã cấu hình ở Phần 2.2 (xác nhận Phần 2.2 hoạt động).
- [ ] **DA.4** — Notebook `00_hello.ipynb` (từ Phần 2.3) gọi hàm từ `check_env.py` bằng `import` thay vì viết lại logic — chứng minh nguyên tắc "logic nằm trong `.py`, notebook chỉ gọi".
- [ ] **DA.5** — Từ 1 thư mục hoàn toàn khác (hoặc nhờ người khác), `git clone` + `uv sync` + `uv run python check_env.py` chạy đúng trong dưới 5 phút, không cần sửa gì.

<details>
<summary><strong>Lời giải chi tiết — Dự án tổng hợp</strong></summary>

**`check_env.py`:**

```python
"""Environment check script for the AI Engineer roadmap.

Run with: uv run python check_env.py
"""
import platform
import sys


def check_package(name: str) -> str:
    """Return the installed version of a package, or 'not installed'."""
    try:
        module = __import__(name)
        return getattr(module, "__version__", "version unknown")
    except ImportError:
        return "not installed"


def check_gpu() -> str:
    """Check GPU availability through PyTorch, if PyTorch is installed."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_count = torch.cuda.device_count()
            return f"Available ({gpu_count} GPU, e.g. {gpu_name})"
        return "Not available (torch installed, no CUDA device found)"
    except ImportError:
        return "Cannot check (torch not installed)"


def build_report() -> dict[str, str]:
    """Collect all environment information into a single dict, so it can
    be both printed by this script and imported/reused from a notebook."""
    return {
        "os": f"{platform.system()} {platform.release()}",
        "cpu_arch": platform.machine(),
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "numpy": check_package("numpy"),
        "pandas": check_package("pandas"),
        "matplotlib": check_package("matplotlib"),
        "torch": check_package("torch"),
        "gpu": check_gpu(),
    }


def print_report(report: dict[str, str]) -> None:
    """Pretty-print the environment report to stdout."""
    print("=" * 50)
    print("AI ENGINEER ENVIRONMENT CHECK")
    print("=" * 50)
    for key, value in report.items():
        print(f"  {key:<18}: {value}")
    print("=" * 50)


if __name__ == "__main__":
    print_report(build_report())
```

**`00_hello.ipynb` — cell gọi lại `check_env.py` (nguyên tắc DA.4):**

```python
# cell 1
from check_env import build_report, print_report

# cell 2 — reuse the exact same logic instead of rewriting it in the notebook
print_report(build_report())

# cell 3 — notebook-only part: visualization
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.title("Hello, AI Engineer roadmap")
plt.show()
```

**`README.md`:**

```markdown
# ai-lab

Repo thực hành cá nhân cho lộ trình AI Engineer — Unit 01.

## Yêu cầu
- [uv](https://docs.astral.sh/uv/) đã cài đặt (tự quản lý Python version, không cần cài Python riêng)

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
- `check_env.py` — script + hàm tái sử dụng kiểm tra môi trường
- `00_hello.ipynb` — notebook thử nghiệm, tái sử dụng logic từ check_env.py
```

**Kiểm chứng DA.5:** trên máy sạch (hoặc container mới):
```bash
git clone <url> test-clone && cd test-clone
time (uv sync && uv run python check_env.py)
# real   0mXX.XXXs   <- phải dưới 5 phút
```
</details>

---

## 6. Đáp án 5 câu tự kiểm tra kiến thức

- [ ] Đã trả lời cả 5 câu bằng lời của chính bạn trong `SUBMISSION.md` trước khi mở phần dưới đây.

<details>
<summary><strong>Đáp án tham khảo</strong></summary>

**Câu 1: Khác nhau venv vs conda?**
> `venv` chỉ cô lập package Python thuần (dựa trên pip), dùng chung Python đã cài trên máy. `conda` là trình quản lý gói đa ngôn ngữ, có thể tự cài cả Python — hữu ích khi cần binary biên dịch phức tạp (CUDA toolkit cũ) mà pip khó build.

**Câu 2: Vì sao cần lock file?**
> `pyproject.toml` chỉ khai báo khoảng version chấp nhận được. Nếu 2 người `pip install` ở 2 thời điểm khác nhau có thể nhận 2 phiên bản khác nhau. Lock file khoá chính xác từng phiên bản (kể cả transitive dependency), đảm bảo mọi người cài đúng 1 bộ gói giống hệt nhau.

**Câu 3: `__pycache__` có nên commit?**
> Không — là artifact tạm thời Python tự sinh, tái tạo tự động, phụ thuộc phiên bản Python đang chạy. Luôn có trong `.gitignore`.

**Câu 4: `PYTHONPATH` dùng làm gì?**
> Liệt kê thêm thư mục Python tìm khi `import`, bổ sung vào danh sách mặc định. Trong dự án có `pyproject.toml` chuẩn, nên ưu tiên cài package ở chế độ editable (`pip install -e .`) thay vì chỉnh `PYTHONPATH` thủ công.

**Câu 5: Colab mất dữ liệu khi nào?**
> Khi máy ảo bị thu hồi sau ~12h hoạt động liên tục hoặc ~90 phút không tương tác (free tier), hoặc bạn chủ động disconnect. Mọi thứ ở `/content/` (không phải `/content/drive/`) sẽ mất — luôn `drive.mount()` và lưu kết quả quan trọng vào Drive.
</details>

---

## 7. Tổng kết & bước tiếp theo

- ✅ Môi trường Python quản lý bằng `uv` duy nhất — nhanh, tái lập được.
- ✅ VS Code cấu hình đúng interpreter, debug được.
- ✅ Repo `ai-lab` hoàn chỉnh — **giữ và mở rộng repo này** cho các bài tiếp theo.

**Bài tiếp theo:** U01-02 — Python core: kiểu dữ liệu & luồng điều khiển.

---

## 8. Ghi điểm (dành cho người chấm)

| Tiêu chí | Điểm tối đa |
|---|---|
| Phần 2.1: môi trường tái lập được, version khớp trước/sau | 2 |
| Phần 2.2: VS Code cấu hình đúng, debug chạy được | 1 |
| Phần 2.3: notebook chạy cả local lẫn Colab | 1 |
| Dự án tổng hợp: `check_env.py` đúng, README rõ ràng, DA.5 chạy < 5 phút | 4 |
| Trả lời đúng ≥4/5 câu hỏi tự kiểm tra | 2 |
| **Tổng** | **10** |

Đạt ≥ 8/10 → tick ☑ ở sheet `U01_Python_CS` trong workmap Excel, ghi ngày hoàn thành và giờ thực tế.
