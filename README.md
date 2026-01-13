# Initials Avatar Generator

Small Python script to generate **PNG avatars with user initials**.  
Designed for quick, manual use (e.g. printer profiles) where default icons are unwanted.

Cross-platform: **Linux + Windows**.

---

## What it does
- generates a 256×256 PNG with 1–2 initials
- deterministic background color based on initials
- automatic text contrast (black/white)
- fixed output name: `etg_XX.png`
- overwrites existing file (intentional)

## What it does NOT do
- no full names
- no custom fonts
- no configuration
- no UI
- no creativity

This is a work tool.

---

## Requirements
- Python 3.9+
- Pillow

### Install Pillow
Linux:
```bash
pip install pillow
```
Windows:
```bash
py -m pip install pillow
```

### Usage
Linux:
```bash
python tworzenie_avatarow.py --user mc
```

Windows:
```bash
py .\tworzenie_avatarow.py --user mc
```
