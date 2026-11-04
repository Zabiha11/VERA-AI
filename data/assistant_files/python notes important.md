# Important Python Documentation Notes

## 1. Getting Started
- **Tutorial** – A step‑by‑step tour of Python’s syntax and core features. Ideal for newcomers.
- **Installation** – Download from https://www.python.org/downloads/. Follow the platform‑specific instructions (Windows, macOS, Linux) and add Python to your `PATH`.
- **Virtual Environments** – Use `python -m venv <env>` to isolate dependencies.

## 2. Language Reference
- **Syntax & Semantics** – Detailed description of statements, expressions, data model, and execution model.
- **Built‑in Functions & Types** – Reference for `len()`, `range()`, `list`, `dict`, `set`, `tuple`, etc.
- **Modules & Packages** – How to import, create packages, and the module search path.

## 3. Standard Library (Library Reference)
- **Collections** – `collections`, `heapq`, `bisect`, `array`.
- **File & I/O** – `os`, `io`, `pathlib`, `shutil`.
- **Data Formats** – `json`, `csv`, `sqlite3`, `xml.etree`.
- **Networking** – `socket`, `http.client`, `urllib`, `asyncio`.
- **Concurrency** – `threading`, `multiprocessing`, `concurrent.futures`.
- **Testing** – `unittest`, `doctest`, `pytest` (third‑party).
- **Utilities** – `logging`, `argparse`, `datetime`, `statistics`.

## 4. How‑to Guides (HOWTOs)
- **Installing Packages** – Use `pip install <package>`; see the *Python Packaging User Guide* for wheels, source builds, and virtual environments.
- **Extending & Embedding** – C/C++ extensions via the Python C API; embedding the interpreter in other applications.
- **Static Typing** – Type hints (`typing` module) and static analysis tools like `mypy`.

## 5. FAQs & Troubleshooting
- Common pitfalls: mutable default arguments, name shadowing, and reference cycles.
- Performance tips: use list comprehensions, built‑ins, and `functools.lru_cache`.

## 6. Additional Resources
- **Developer’s Guide** – Contributing to CPython, code style, and testing.
- **PEP Index** – Official proposals that shape the language.
- **Audio/Visual Talks** – Recorded talks from PyCon and other conferences.
- **Glossary** – Definitions of key terms.

*All information is taken from the official Python 3.15.2 documentation (https://docs.python.org/3/).*
