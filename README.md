# Excel Filter (PyQt6 + openpyxl, Python 3.9)

Language:
</br>
1. [ENG version](#ENG)
</br>
2. [RU version](#RU)

---

## ENG

---

A small, cross-platform desktop utility that:

* opens an Excel `.xlsx` file,
* **filters rows** where a user-selected **column equals a user-entered value** (case-insensitive, including Cyrillic),
* keeps **only** the columns: **`ФИО`, `Должность`, `Отдел`, `Дата найма`, `Зарплата`**,
* saves the result to a **new `.xlsx`**.

The app ships with a simple **PyQt6 GUI** and uses **openpyxl** for Excel I/O. It runs on **Windows** and **Linux** (including **WSLg** under Windows).

---

## Table of Contents

* [Features](#features)
* [Screenshots](#screenshots)
* [How it works (high level)](#how-it-works-high-level)
* [Requirements](#requirements)
* [Quick Start](#quick-start)

  * [Windows (Python 3.9 + venv)](#windows-python-39--venv)
  * [Linux / WSL (Python 3.9 + venv)](#linux--wsl-python-39--venv)
* [Using the App](#using-the-app)
* [Case-insensitive matching](#case-insensitive-matching)
* [Date handling](#date-handling)
* [Automatic header detection](#automatic-header-detection)
* [Output workbook details](#output-workbook-details)
* [Error messages & UX](#error-messages--ux)
* [Packaging (distributables)](#packaging-distributables)

  * [Windows EXE (PyInstaller)](#windows-exe-pyinstaller)
  * [Linux binary (PyInstaller)](#linux-binary-pyinstaller)
  * [What to share vs what to commit](#what-to-share-vs-what-to-commit)
* [Run on Linux via WSLg / X server](#run-on-linux-via-wslg--x-server)
* [Project layout & helpful files](#project-layout--helpful-files)
* [Troubleshooting](#troubleshooting)
* [FAQ](#faq)
* [License](#license)

---

## Features

* **GUI**: Browse for input/output files, choose a column, type a value, click “Filter”.
* **Robust header detection**: Finds the actual header row even if the file has a multi-row preamble.
* **Insensitive to case/spacing**: Compares text using `casefold()` (better than `lower()` for international text).
* **Dates that “just work”**: Recognizes dates both as true Excel dates and as text like `30.10.2014`, `2014-10-30`, `30/10/2014`.
* **Deterministic output**: Keeps only `ФИО`, `Должность`, `Отдел`, `Дата найма`, `Зарплата` (in that order).
* **Cross-platform**: Windows & Linux (incl. WSLg). No OS-specific paths in code.
* **Friendly logging**: In-app log shows what happened. Clear errors for common pitfalls (e.g., output file open in Excel).

---

## How it works (high level)

1. **Open file** → read with `openpyxl.load_workbook(..., read_only=True, data_only=True)`.
2. **Detect header row** (see [Automatic header detection](#automatic-header-detection)).
3. **Build a header map**: `normalized name → column index`. Normalization = `strip + casefold`.
4. **Filter**: for each data row, compare the selected column’s value to the user input.

   * Text: compare normalized strings (case-insensitive).
   * Dates: both sides normalized to ISO (`YYYY-MM-DD`), even if Excel stored the date as text.
5. **Keep only** the five required columns and **save** to a new `.xlsx`.
6. **Log** what happened (counts, missing required columns, etc.).

---

## Requirements

* **Python 3.9** (as per assignment)
* **pip**
* Python dependencies:

  * `PyQt6`
  * `openpyxl`

> Minimal `requirements.txt`:
>
> ```
> PyQt6==6.7.1
> openpyxl==3.1.5
> ```

---

## Quick Start

### Windows (Python 3.9 + venv)

```powershell
# from project root
py -3.9 -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# run
python main.py
```

### Linux / WSL (Python 3.9 + venv)

```bash
# from project root
python3.9 -m venv .venv     # or use pyenv to install 3.9.x
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# run
python main.py
```

> **WSL users (Windows 11 / WSLg)**: GUI windows appear like native Windows apps—no extra setup.
> **Windows 10 (no WSLg)**: You’ll need an X server (e.g., VcXsrv) — see [Run on Linux via WSLg / X server](#run-on-linux-via-wslg--x-server).

---

## Using the App

1. **Input .xlsx**: click **“Выбрать файл…”** and pick your Excel file.
2. The app **detects the header row** and fills the **“Столбец”** dropdown.
3. **Choose a column** (e.g., *Отдел*).
4. **Enter a value** (e.g., `разработка`, `Разработка`, `РАЗРАБОТКА` — all match).
5. **Output path**: click **“Сохранить как…”** (or accept the suggested `*_filtered.xlsx`).
6. Click **“Выполнить фильтрацию”**.
7. Open the output file in Excel/LibreOffice. You’ll see **only** the five required columns, filtered rows.

---

## Case-insensitive matching

* We normalize strings with `str(x).strip().casefold()`.
* `casefold()` is stronger than `lower()` for international text (e.g., Cyrillic).
* Matching is by **equality** (not contains). If you need partial matches later, you can adapt the comparison.

---

## Date handling

* Input box accepts:

  * `DD.MM.YYYY` (e.g., `30.10.2014`)
  * `YYYY-MM-DD` (e.g., `2014-10-30`)
  * `DD/MM/YYYY` (e.g., `30/10/2014`)
* Column values can be:

  * **true Excel dates** (`datetime/date`) → normalized to `YYYY-MM-DD`, or
  * **text dates** (e.g., `"30.10.2014"`) → parsed & normalized to `YYYY-MM-DD`.
* The comparison uses normalized ISO strings; this makes text dates and real dates behave the same.
* In the **output**, the “Дата найма” column is written as real dates (when possible) and formatted as `DD.MM.YYYY`.

> **Note about `#####` in Excel**: If you see `########` in a date/number cell, it’s just a **column width** issue. Widen the column; the underlying value is intact.

---

## Automatic header detection

Real-world Excel files often have a preamble (“Тип”, “Дата выгрузки”, etc.). We don’t assume row 1 is the header. Instead:

* We scan the first **N** rows (default \~25–50).
* For each row, compute a **score**:

  * `score = (# non-empty cells) + 2 × (# matches among expected names)`
* “Expected names” include (normalized): `фио`, `должность`, `отдел`, `дата найма`, `зарплата`.
* We pick the row with the **highest score** as the **header row**.
* Data starts at **header\_row + 1**.

This heuristic handles common preambles while remaining fast and simple.

---

## Output workbook details

* Sheet name: **`Результат`**
* First row: exactly the five headers, **in fixed order**:
  `ФИО`, `Должность`, `Отдел`, `Дата найма`, `Зарплата`
  (Only those present in the source are included; missing ones are reported in the log.)
* Data rows: only rows that matched the filter.
* “Дата найма” cells are real dates when possible (`number_format = "DD.MM.YYYY"`).

---

## Error messages & UX

* The app logs to the **Log** panel (at the bottom).
* Typical user-friendly messages:

  * **Missing selections** (“Input file not chosen”, “No output path”, “Column not chosen”).
  * **Column not found** in the file.
  * **Output file is open** (Excel/LibreOffice) → `PermissionError` with a clear hint to close the file.
  * **No matches** → the output file is still created (header only) with a warning.
* (Optional) You can also show `QMessageBox` popups for warnings/info.

---

## Packaging (distributables)

> Build **on the target OS**:
>
> * Build **Windows EXE** on Windows.
> * Build **Linux binary** on Linux/WSL.

### Windows EXE (PyInstaller)

From project root in **PowerShell** (inside your venv):

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name ExcelFilter main.py
# artifact: .\dist\ExcelFilter.exe
```

* `--onefile`: single `.exe` containing Python runtime + your code + libs.
* `--windowed`: no console window.
* If PyQt6 triggers hidden-import issues (rare), add:

  ```
  --hidden-import PyQt6.sip --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtWidgets
  ```

**Zip it**:

```powershell
Compress-Archive -Path .\dist\ExcelFilter.exe -DestinationPath ExcelFilter_Windows.zip
```

### Linux binary (PyInstaller)

From **WSL/Linux**:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name excel-filter main.py
# artifact: ./dist/excel-filter

# zip
cd dist
zip -9 ../ExcelFilter_Linux.zip excel-filter
```

> The **Windows `.exe`** only runs on Windows.
> The **Linux ELF** only runs on Linux.

### What to share vs what to commit

* Share **the built artifact** (e.g., `dist/ExcelFilter.exe` or `dist/excel-filter`) in a release/zip.
* Do **not** commit build artifacts to Git. Keep the repo clean (source only).

---

## Run on Linux via WSLg / X server

**WSLg (Windows 11 or WSL from Microsoft Store):**
Just run `python main.py` in WSL—GUI windows appear like native apps. Nothing else to set up.

**Windows 10 (no WSLg):**
Install an X server on Windows (e.g., **VcXsrv**), run it, then set in WSL:

```bash
export DISPLAY=$(grep -oP '(?<=nameserver\s)\S+' /etc/resolv.conf):0.0
python main.py
```

---

## Project layout & helpful files

```
project/
├─ main.py                # the app
├─ requirements.txt       # PyQt6 + openpyxl
├─ README.md              # this file
├─ .gitignore             # ignore build/venv/caches
└─ docs/                  # (optional) screenshots for README
```

**Suggested `.gitignore`:**

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
env/
*.log

# PyInstaller
/dist/
/build/
*.spec

# IDE
.idea/
.vscode/

# OS
.DS_Store
Thumbs.db

# Data (example policy)
*.xlsx
!sample.xlsx
```

---

## Troubleshooting

**Excel shows `########` in date/number cells**
→ Column is too narrow. Widen it. The underlying value is correct; Python will read the real value (not hashes).

**“PermissionError” when saving**
→ Output file is likely open in Excel/LibreOffice. Close it and try again.

**Column not in dropdown / wrong header row**

* The file may have a long preamble. The heuristic scans only the top N rows (configurable in `_guess_header_row(ws, search_limit=...)`).
* Ensure the real header row contains meaningful, non-empty names.

**No matches found**

* The comparison is **equality**, not substring.
* Check for leading/trailing spaces (we strip), spelling, or try another date format.
* Date input must be one of: `DD.MM.YYYY`, `YYYY-MM-DD`, `DD/MM/YYYY`.

**App doesn’t start on Linux (WSL)**

* On Windows 11 WSLg: update WSL via Microsoft Store.
* On Windows 10: run an X server (VcXsrv) and set `DISPLAY`.

---

## FAQ

**Q: Can I filter by partial text (contains)?**
A: Not in the base version. You can change the equality check to `if value_norm in cell_norm:` to support “contains”.

**Q: Can I add more required columns to the output?**
A: Yes. Update the constant list (e.g., `REQUIRED_OUT_HEADERS = [...]`) and ensure header detection still recognizes your names.

**Q: Will the app modify my input file?**
A: No. It’s opened read-only; the result goes to a new file.

**Q: Does the output preserve formatting?**
A: Only basic formatting is applied (date number format). Advanced styling is intentionally minimal.

**Q: Do I need Python to run the packaged `exe`?**
A: No. The `.exe` contains a Python runtime and required libraries.

---

## License

Choose a license and add it to `LICENSE` (e.g., MIT):

```text
MIT License
Copyright (c) 2025 ...

Permission is hereby granted, free of charge, to any person obtaining a copy
...
```

---

## RU

---

# Excel Filter (PyQt6 + openpyxl, Python 3.9)

Небольшая кроссплатформенная утилита, которая:

* открывает Excel-файл `.xlsx`,
* **фильтрует строки** по принципу: выбранный пользователем **столбец = введённому значению** (без учёта регистра, работает с кириллицей),
* оставляет **только** столбцы: **`ФИО`, `Должность`, `Отдел`, `Дата найма`, `Зарплата`**,
* сохраняет результат в **новый `.xlsx`**.

Графический интерфейс — на **PyQt6**, чтение/запись Excel — через **openpyxl**. Приложение работает на **Windows** и **Linux** (в том числе в **WSLg** под Windows).

---

## Содержание

* [Возможности](#возможности)
* [Скриншоты](#скриншоты)
* [Как это работает (в общих чертах)](#как-это-работает-в-общих-чертах)
* [Требования](#требования)
* [Быстрый старт](#быстрый-старт)

  * [Windows (Python 3.9 + venv)](#windows-python-39--venv)
  * [Linux / WSL (Python 3.9 + venv)](#linux--wsl-python-39--venv)
* [Как пользоваться](#как-пользоваться)
* [Сопоставление без учёта регистра](#сопоставление-без-учёта-регистра)
* [Работа с датами](#работа-с-датами)
* [Автоопределение строки заголовков](#автоопределение-строки-заголовков)
* [Подробности выходной книги](#подробности-выходной-книги)
* [Сообщения об ошибках и UX](#сообщения-об-ошибках-и-ux)
* [Сборка дистрибутивов](#сборка-дистрибутивов)

  * [Windows EXE (PyInstaller)](#windows-exe-pyinstaller)
  * [Linux-бинарник (PyInstaller)](#linux-бинарник-pyinstaller)
  * [Что публиковать, а что коммитить](#что-публиковать-а-что-коммитить)
* [Запуск на Linux через WSLg / X-сервер](#запуск-на-linux-через-wslg--x-сервер)
* [Структура проекта и полезные файлы](#структура-проекта-и-полезные-файлы)
* [Troubleshooting](#troubleshooting)
* [FAQ](#faq)
* [Лицензия](#лицензия)

---

## Возможности

* **GUI**: выбор входного/выходного файла, списка столбцов, введение значения, кнопка «Выполнить».
* **Устойчивое чтение заголовков**: находит реальную строку шапки, даже если вверху много служебных строк.
* **Сопоставление без регистра и лишних пробелов**: используем `casefold()` (надёжнее `lower()` для интернационального текста).
* **Даты «как надо»**: распознаются как настоящие Excel-даты, так и текстовые строки вида `30.10.2014`, `2014-10-30`, `30/10/2014`.
* **Детерминированный результат**: в выходном файле только `ФИО`, `Должность`, `Отдел`, `Дата найма`, `Зарплата` — именно в этом порядке.
* **Кроссплатформенность**: Windows и Linux (вкл. WSLg). В коде нет ОС-зависимых путей.
* **Дружелюбные сообщения**: лог показывает действия и ошибки (например, «файл результата открыт в Excel»).

---

## Как это работает (в общих чертах)

1. **Открываем файл** через `openpyxl.load_workbook(..., read_only=True, data_only=True)`.
2. **Определяем строку заголовков** (см. раздел ниже).
3. **Строим карту заголовков**: «нормализованное имя → индекс столбца». Нормализация = `strip + casefold`.
4. **Фильтруем**: для каждой строки данных сравниваем значение в выбранном столбце с пользовательским вводом.

   * Текст: сравнение нормализованных строк (без регистра).
   * Даты: обе стороны приводим к ISO-формату `YYYY-MM-DD`, даже если дата хранится как текст.
5. **Оставляем только** пять нужных столбцов и **сохраняем** новый `.xlsx`.
6. **Логируем** действия и результат (сколько строк, какие колонки отсутствуют и т. п.).

---

## Требования

* **Python 3.9** (по условию задачи)
* **pip**
* Зависимости Python:

  * `PyQt6`
  * `openpyxl`

> Минимальный `requirements.txt`:
>
> ```
> PyQt6==6.7.1
> openpyxl==3.1.5
> ```

---

## Быстрый старт

### Windows (Python 3.9 + venv)

```powershell
# из корня проекта
py -3.9 -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# запуск
python main.py
```

### Linux / WSL (Python 3.9 + venv)

```bash
# из корня проекта
python3.9 -m venv .venv     # либо поставьте 3.9 через pyenv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# запуск
python main.py
```

> **WSL (Windows 11 / WSLg)**: окна GUI показываются как обычные приложения Windows — ничего дополнительно настраивать не нужно.
> **Windows 10 (без WSLg)**: потребуется X-сервер (например, VcXsrv) — см. раздел ниже.

---

## Как пользоваться

1. Нажмите **«Выбрать файл…»** и укажите входной `.xlsx`.
2. Приложение **автоматически определит строку заголовков** и заполнит выпадающий список **«Столбец»**.
3. Выберите столбец (например, *Отдел*).
4. Введите значение (например, `разработка` / `РАЗРАБОТКА` — регистр не важен).
5. Укажите путь для сохранения результата (или оставьте предложенный `*_filtered.xlsx`).
6. Нажмите **«Выполнить фильтрацию»**.
7. Откройте выходной файл в Excel/LibreOffice: вы увидите **только** пять нужных столбцов и отфильтрованные строки.

---

## Сопоставление без учёта регистра

* Строки нормализуются через `str(x).strip().casefold()`.
* `casefold()` — «усиленная» форма `lower()` и лучше работает для интернационального текста (в т. ч. кириллицы).
* Сравнение по **равенству** (не «содержит»). Если нужно — логику легко заменить на частичное совпадение.

---

## Работа с датами

* Поле ввода принимает форматы:

  * `DD.MM.YYYY` (напр., `30.10.2014`)
  * `YYYY-MM-DD` (напр., `2014-10-30`)
  * `DD/MM/YYYY` (напр., `30/10/2014`)
* В столбце могут быть:

  * **настоящие Excel-даты** (`datetime`/`date`) → приводим к `YYYY-MM-DD`,
  * **текстовые даты** (напр., `"30.10.2014"`) → распознаём и тоже приводим к `YYYY-MM-DD`.
* Сравнение делается по ISO-строкам, поэтому текстовые и настоящие даты сравниваются одинаково.
* В **результате** «Дата найма» записывается как настоящая дата (когда возможно) с форматом `DD.MM.YYYY`.

> **Замечание про `#####` в Excel**: если в ячейке видно `########`, это **узкий столбец**, а не испорченные данные. Расширьте колонку — значение на месте. Python при чтении получит истинные значения, не `#`.

---

## Автоопределение строки заголовков

В реальных Excel часто есть «шапка»/пояснения сверху («Тип», «Дата выгрузки» и т. п.). Мы **не предполагаем**, что заголовки — в первой строке. Вместо этого:

* Сканируем первые **N** строк (обычно 25–50).
* Для каждой строки считаем **балл**:

  * `балл = (кол-во непустых ячеек) + 2 × (кол-во совпадений с ожидаемыми именами)`
* «Ожидаемые имена» (нормализованные): `фио`, `должность`, `отдел`, `дата найма`, `зарплата`.
* Берём строку с **максимальным баллом** как **строку заголовков**.
* Данные начинаются с **header\_row + 1**.

Эта простая эвристика хорошо справляется с прелюдиями и работает быстро.

---

## Подробности выходной книги

* Имя листа: **`Результат`**.
* Первая строка: ровно 5 заголовков **в фиксированном порядке**:
  `ФИО`, `Должность`, `Отдел`, `Дата найма`, `Зарплата`
  (Если каких-то нет во входном файле, они не попадут в результат; это отразится в логе.)
* Данные: только строки, прошедшие фильтр.
* «Дата найма» — настоящая дата (если возможно) с числовым форматом `DD.MM.YYYY`.

---

## Сообщения об ошибках и UX

* Все действия пишутся в **лог** (нижняя панель).
* Типичные сообщения:

  * **Не выбран** входной файл/путь сохранения/столбец.
  * **Столбец не найден** в файле (если пользователь выбрал то, чего в исходнике нет).
  * **Файл результата открыт** (Excel/LibreOffice) → `PermissionError` и подсказка закрыть файл.
  * **Совпадений нет** → файл всё равно создаётся (только шапка) + предупреждение.
* (Опционально) для важных событий показываем `QMessageBox` (всплывающие окна).

---

## Сборка дистрибутивов

> Собирать нужно **под целевую ОС**:
>
> * Windows-exe — на Windows,
> * Linux-бинарь — на Linux/WSL.

### Windows EXE (PyInstaller)

Из корня проекта в **PowerShell** (внутри вашего venv):

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name ExcelFilter main.py
# артефакт: .\dist\ExcelFilter.exe
```

Пояснения:

* `--onefile` — один `.exe`, внутри Python + ваши зависимости.
* `--windowed` — без консольного окна.
* Если PyQt6 вдруг потребует скрытые импорты (редко), добавьте:

  ```
  --hidden-import PyQt6.sip --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtWidgets
  ```

**Запаковать в zip:**

```powershell
Compress-Archive -Path .\dist\ExcelFilter.exe -DestinationPath ExcelFilter_Windows.zip
```

### Linux-бинарник (PyInstaller)

Из **WSL/Linux**:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name excel-filter main.py
# артефакт: ./dist/excel-filter

# zip
cd dist
zip -9 ../ExcelFilter_Linux.zip excel-filter
```

> **Важно:** Windows-`.exe` работает только на Windows. Linux-ELF — только на Linux.

### Что публиковать, а что коммитить

* Публикуйте **собранные артефакты** (напр., `dist/ExcelFilter.exe`, `dist/excel-filter`) в релизах/zip.
* **Не коммитьте** сборочные файлы в git — репозиторий держим «чистым» (только исходники).

---

## Запуск на Linux через WSLg / X-сервер

**WSLg (Windows 11 или WSL из Microsoft Store):**
Просто запускайте `python main.py` в WSL — окна GUI появятся как обычные Windows-приложения.

**Windows 10 (без WSLg):**
Поставьте X-сервер в Windows (например, **VcXsrv**), запустите его, затем в WSL:

```bash
export DISPLAY=$(grep -oP '(?<=nameserver\s)\S+' /etc/resolv.conf):0.0
python main.py
```

---

## Структура проекта и полезные файлы

```
project/
├─ main.py                # приложение
├─ requirements.txt       # PyQt6 + openpyxl
├─ README.md              # этот файл
├─ .gitignore             # исключения для git
└─ docs/                  # (опционально) скриншоты для README
```

**Рекомендуемый `.gitignore`:**

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
env/
*.log

# PyInstaller
/dist/
/build/
*.spec

# IDE
.idea/
.vscode/

# OS
.DS_Store
Thumbs.db

# Data (пример политики)
*.xlsx
!sample.xlsx
```

---

## Troubleshooting

**В ячейках даты/числа видны `########`**
→ Узкий столбец. Увеличьте ширину — данные не повреждены. При чтении из Python вернутся настоящие значения.

**“PermissionError” при сохранении**
→ Файл результата открыт в Excel/LibreOffice. Закройте его и повторите сохранение.

**Нет нужного столбца в выпадающем списке / неверная строка заголовков**

* Во входнике может быть длинная «шапка». Эвристика сканирует первые N строк (можно увеличить параметр `search_limit` в `_guess_header_row`).
* Убедитесь, что реальная строка заголовков не пустая и содержит осмысленные имена.

**Совпадений нет**

* Сравнение по **равенству** (не «содержит»).
* Проверьте лишние пробелы (мы обрезаем), орфографию, попробуйте другой формат даты.
* Поддерживаются форматы ввода дат: `DD.MM.YYYY`, `YYYY-MM-DD`, `DD/MM/YYYY`.

**Приложение не стартует на Linux (WSL)**

* В Windows 11 обновите WSL (через Microsoft Store).
* В Windows 10 запустите X-сервер (VcXsrv) и установите `DISPLAY`.

---

## FAQ

**Можно фильтровать по частичному совпадению?**
Базовая версия — по равенству. Измените проверку на `if value_norm in cell_norm:` — получите «содержит».

**Как добавить дополнительные колонки в результат?**
Измените список `REQUIRED_OUT_HEADERS = [...]` и убедитесь, что автоопределение заголовков их распознаёт.

**Изменится ли входной файл?**
Нет. Он открывается в режиме `read_only=True`. Результат всегда пишется в новый файл.

**Сохраняется ли форматирование?**
Мы сознательно делаем минимальное форматирование (только формат дат). Стили/ширины столбцов не настраиваем, чтобы код оставался простым.

**Нужен ли Python на машине пользователя для запуска `.exe`?**
Нет. PyInstaller пакует в `.exe` Python и все зависимости.

---

## Лицензия

Выберите лицензию и добавьте файл `LICENSE` (например, MIT):

```text
MIT License
Copyright (c) ...

Permission is hereby granted, free of charge, to any person obtaining a copy
...
```

---
