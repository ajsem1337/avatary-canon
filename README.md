# Avatars from initials

![Made with AI](https://raw.githubusercontent.com/ajsem1337/ajsem1337/main/assets/made-with-ai.svg)

A local script that creates 256 × 256 px PNG avatars from initials, for example for printer user profiles, without accounts or external services.

## Installation

Requirements: Python 3.11+ and Pillow 13.0+. Run the commands in the repository directory.

Pillow 13 does not support Python 3.9 or 3.10. Upgrade to Python 3.11 or newer
before updating dependencies; see the
[Pillow compatibility note](https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html#python-3-10).

Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tworzenie_avatarow.py --user mc
```

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\tworzenie_avatarow.py --user mc
```

The script prints the path to the generated file:

```text
avatary/etg_MC.png
```

Windows paths use the `\` separator. If Linux reports that `venv` is missing,
install the package that provides it for your distribution.

## Usage

The examples below use the interpreter from the Linux `.venv` environment.
On Windows, replace `.venv/bin/python` with `.\.venv\Scripts\python.exe`.

```sh
.venv/bin/python tworzenie_avatarow.py --user "łż"
.venv/bin/python tworzenie_avatarow.py --user mc --outdir "gotowe awatary"
.venv/bin/python tworzenie_avatarow.py --help
```

| Argument | Purpose |
| --- | --- |
| `--user` | Required. Text used to generate the initials. |
| `--outdir` | Output directory, defaulting to `avatary`. Created automatically. |

The output directory is relative to the terminal's current directory.
The filename is `etg_<INICJAŁY>.png`, where `<INICJAŁY>` means the uppercase initials.
**An existing file with that name is overwritten without prompting.**

## How avatars are generated

- Text is converted to uppercase. Spaces and non-alphanumeric characters are
  removed, and the first two characters are kept. `m-c` produces `MC`; `7` produces `7`.
- The script does not extract initials from full names: `Jan Kowalski` produces `JA`.
- Equivalent Unicode representations are normalized before filtering characters.
- The background color comes from a SHA-256 hash of the initials. The same initials
  produce the same background.
- Text is black or white, whichever gives greater
  [contrast against the background](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum).
- Images are saved as RGB PNGs without transparency.

The script uses Pillow's font lookup, which searches system directories on
Linux, Windows and macOS, as well as user directories and XDG settings on Linux.
It tries DejaVu Sans Bold, Liberation Sans Bold, Noto Sans Bold, Segoe UI Bold,
Arial Bold and Calibri Bold in that order, followed by Arial Bold for macOS.
If none is found, it uses Pillow's built-in font, whose
[scaling requires Pillow 10.1+](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.load_default).
The built-in font has a limited character set; for Polish letters, install one
of the listed system fonts. The selected font may not support every character
accepted by `--user`.

Letter shapes depend on the available font and Pillow version. Images generated
on different computers may look different even with the same initials.

## Errors and tests

Exit code `0` means success; `2` means invalid arguments or no letters/digits in
`--user`; `1` means image creation or writing failed. Check the error message,
directory path and write permissions.

Tests use `unittest` and require no libraries beyond Pillow:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

They cover initials normalization, contrast, text centering and fitting,
missing system fonts, and CLI behavior, including overwrites and write errors.

---

<p align="center"><sub>Built by <a href="https://github.com/ajsem1337">ajsem</a> with AI assistance.</sub></p>
