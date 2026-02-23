<div align="center">
  
# [LaTeX-Reviewer.](https://github.com/BrenoFariasdaSilva/LaTeX-Reviewer) <img src="https://github.com/BrenoFariasdaSilva/LaTeX-Reviewer/blob/e615fe5f90db842738521d75ae2738781348f2b8/.assets/Icons/LaTeX.png"  width="3%" height="3%">

</div>

<div align="center">
  
---

Analyzes LaTeX projects by scanning `.tex` files under the configured `ROOT_PATH`. Detects a defined set of issues implemented in the code: unresolved references, repeated parentheses, first-person pronouns, improper apostrophes, decimal formatting and precision, double whitespace, glossary plural misuse, unescaped underscores, percentage formatting, missing section labels, missing BibTeX entries, mixed numeric representations, itemize punctuation inconsistencies, duplicate citations, and spelling issues.

Where the implementation defines deterministic, unambiguous fixes the script updates files in-place and preserves indentation and commented content. It also performs heuristic checks against a compiled PDF for rendered issues (unresolved references, repeated parentheses, glossary indications). All findings and applied fixes are written to the JSON report at the `OUTPUT_REPORT` path; spelling suggestions are produced via `SpellChecker` but are not auto-applied. The script redirects `stdout`/`stderr` to the repository `Logger` and may register a platform-dependent sound callback on exit when enabled.

---

</div>

<div align="center">

![GitHub Code Size in Bytes](https://img.shields.io/github/languages/code-size/BrenoFariasdaSilva/LaTeX-Reviewer)
![GitHub Commits](https://img.shields.io/github/commit-activity/t/BrenoFariasDaSilva/LaTeX-Reviewer/main)
![GitHub Last Commit](https://img.shields.io/github/last-commit/BrenoFariasdaSilva/LaTeX-Reviewer)
![GitHub Forks](https://img.shields.io/github/forks/BrenoFariasDaSilva/LaTeX-Reviewer)
![GitHub Language Count](https://img.shields.io/github/languages/count/BrenoFariasDaSilva/LaTeX-Reviewer)
![GitHub License](https://img.shields.io/github/license/BrenoFariasdaSilva/LaTeX-Reviewer)
![GitHub Stars](https://img.shields.io/github/stars/BrenoFariasdaSilva/LaTeX-Reviewer)
![GitHub Contributors](https://img.shields.io/github/contributors/BrenoFariasdaSilva/LaTeX-Reviewer)
![GitHub Created At](https://img.shields.io/github/created-at/BrenoFariasdaSilva/LaTeX-Reviewer)
![wakatime](https://wakatime.com/badge/github/BrenoFariasdaSilva/LaTeX-Reviewer.svg)

</div>

<div align="center">
  
![RepoBeats Statistics](https://repobeats.axiom.co/api/embed/cf02a5289d0c91ccb0328f0ac0d5adbad3e33f1e.svg "Repobeats analytics image")

</div>

## Table of Contents
- [LaTeX-Reviewer. ](#latex-reviewer-)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Requirements](#requirements)
  - [Setup](#setup)
    - [Clone the repository](#clone-the-repository)
  - [Installation:](#installation)
  - [Run Programing Language Code:](#run-programing-language-code)
    - [Dependencies](#dependencies)
  - [Usage](#usage)
  - [Results](#results)
  - [How to Cite?](#how-to-cite)
  - [Contributing](#contributing)
  - [Collaborators](#collaborators)
  - [License](#license)
    - [Apache License 2.0](#apache-license-20)

## Introduction

Automatically detects and fixes common LaTeX writing and formatting issues in academic papers. The code operates directly on LaTeX source files (.tex) under a configured root path, preserves formatting and comments when making safe deterministic auto-fixes, and produces a machine-readable JSON report of findings and applied fixes.

The implementation includes functions for file-system discovery of .tex sources, rendered-output heuristics against a compiled PDF, BibTeX key extraction, per-line analysis for a set of explicit checks, and in-place application of unambiguous fixes.

## Requirements

- Python >= 3.9 (documented in the script docstring)
- Standard-library modules imported by the script: `atexit`, `datetime`, `json`, `os`, `platform`, `re`, `sys`, `functools`, `pathlib`
- Third-party modules imported by the script: `colorama`, `spellchecker` (the script imports `from spellchecker import SpellChecker`)
- A local module present in the repository: `Logger.py` (imported as `from Logger import Logger`)

## Setup

### Clone the repository

1. Clone the repository with the following command:

   ```bash
   git clone https://github.com/BrenoFariasDaSilva/LaTeX-Reviewer.git
   cd LaTeX-Reviewer
   ```

## Installation:

* Programing Language:

  * Manually:

   Linux (Debian/Ubuntu):

   ```bash
   sudo apt update
   sudo apt install python3 python3-pip -y
   ```

   Linux (Fedora/CentOS):

   ```bash
   sudo dnf install python3 python3-pip -y
   ```

   macOS (Homebrew):

   ```bash
   brew update
   brew install python
   ```

   Windows (Chocolatey, run from elevated PowerShell):

   ```powershell
   choco install python -y
   ```

   Windows (official installer):

   Visit https://www.python.org/downloads/ and download the Windows installer, then run it manually.

  * Using Makefile:
      ```bash
      make install
      ```

  * Using ShellScript:
      ```bash
      chmod +x install_dependencies.sh
      ./install_dependencies.sh
      ```  

## Run Programing Language Code:

```bash
python3 main.py
```

### Dependencies

The script imports the following modules; install the third-party modules before running:

- `colorama` (imported as `from colorama import Style`)
- `spellchecker` (imported as `from spellchecker import SpellChecker`)

The script also requires the repository-local `Logger.py` module which is imported at runtime.

Standard-library modules used (no installation required): `atexit`, `datetime`, `json`, `os`, `platform`, `re`, `sys`, `functools`, `pathlib`.
