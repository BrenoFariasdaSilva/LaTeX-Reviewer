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
  - [Verifications](#verifications)
  - [Requirements](#requirements)
  - [Setup](#setup)
    - [Clone the repository](#clone-the-repository)
  - [Installation:](#installation)
  - [Run Programing Language Code:](#run-programing-language-code)
    - [Dependencies](#dependencies)
  - [Usage](#usage)
    - [Command-line arguments](#command-line-arguments)
  - [Results](#results)
  - [How to Cite?](#how-to-cite)
  - [Contributing](#contributing)
  - [Collaborators](#collaborators)
  - [License](#license)
    - [Apache License 2.0](#apache-license-20)

## Introduction

Automatically detects and fixes common LaTeX writing and formatting issues in academic papers. The code operates directly on LaTeX source files (.tex) under a configured root path, preserves formatting and comments when making safe deterministic auto-fixes, and produces a machine-readable JSON report of findings and applied fixes.

The implementation includes functions for file-system discovery of .tex sources, rendered-output heuristics against a compiled PDF, BibTeX key extraction, per-line analysis for a set of explicit checks, and in-place application of unambiguous fixes.

## Verifications

The implementation performs the following verifications (report key shown in parentheses) and documents whether the check modifies files or only reports findings:

- **Unresolved references** (`unresolved_references`): detects `??` in `.tex` lines and in the compiled PDF; reports only.
- **Repeated left parentheses** (`repeated_left_parentheses`) and **repeated right parentheses** (`repeated_right_parentheses`): detects occurrences of `((` and `))` in `.tex` lines and in the compiled PDF; reports only.
- **First-person pronouns** (`pronouns`): detects configured pronoun regexes for English and Portuguese (pt-br) in non-commented source lines; reports only.
- **Apostrophe issues** (`apostrophes`): detects common apostrophe problems in source lines; reports only.
- **Decimal formatting** and **decimal precision** (`decimal_formatting`, `decimal_precision`): extracts decimal numbers from lines and reports formatting or precision inconsistencies; reports only.
- **Double whitespace** (`double_whitespace`): detects consecutive intra-line whitespace; automatic in-place correction is applied when unambiguous.
- **Glossary plural misuse** (`glossary_plural`): verifies `\gls{...}` usages against labels loaded from `entradas-siglas.tex`; reports mismatches and the code contains an auto-fix routine for certain plural cases (modifies files in-place when applied).
- **Underscore misuse** (`underscore_misuse`): detects unescaped underscores in text and applies in-place fixes where safe.
- **Percentage misuse** (`percentage_misuse`): detects improper percentage formatting and applies in-place fixes where safe.
- **Missing section labels** (`missing_section_label`): detects section/chapter/subsection headings without a following `\label{}` and inserts a generated label of the form `\label{sec:<sanitized-title>}` on the next line; auto-fix applied in-place.
- **Missing BibTeX entries** (`missing_bib_entries`): detects `\cite{...}` keys not present in the configured BibTeX file (`main.bib`); reports only.
- **Mixed numeric representation** (`numeric_representation`): detects contexts with inconsistent numeric styles (digits versus words); reports only.
- **Itemize punctuation** (`itemize_punctuation`): inspects `itemize` items for terminal punctuation consistency and performs deterministic in-place fixes when applicable.
- **Duplicate citations** (`duplicate_citations`): deduplicates keys inside the same `\cite{...}` block and writes the corrected citation back to the file; auto-fix applied in-place.
- **Spelling** (`spelling`): produces spelling suggestions via `SpellChecker`; suggestions are recorded in the report but are not automatically applied to source files.

Where automatic corrections are applied the script preserves indentation and never modifies fully commented lines. The implementation also runs a small set of heuristic rendered-output checks against the compiled PDF (unresolved references, repeated parentheses, glossary indications) and records findings in the JSON report. All findings and any applied fixes are written to the JSON report at the `OUTPUT_REPORT` path. The script redirects `stdout`/`stderr` to the repository `Logger` and may register a platform-dependent sound callback on exit when enabled.

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

## Usage

In order to run the program as implemented in `main.py`:

- Option A — via Makefile (if a `make run` target exists):

```bash
make run
```

- Option B — directly with Python (the file defines `if __name__ == "__main__": main()`):

```bash
python3 main.py
```
Configuration notes (literal variables in the code):

- `ROOT_PATH` (default set in the file to `./Input/SBC Paper/`) — root directory searched for `.tex` files.
- `OUTPUT_REPORT` (default set to `f"{ROOT_PATH}latex_review_report.json"`) — path where the JSON report is written. When `--root-path` is provided at runtime `OUTPUT_REPORT` is updated to `f"{ROOT_PATH}latex_review_report.json"` using the effective `ROOT_PATH`.

### Command-line arguments

Command-line arguments (implemented in `main.py`):

- `--verbose` (optional): enable verbose output. Type: flag (`store_true`). Default: not provided → `VERBOSE` remains `False` (no verbose output).

- `--root-path <path>` (optional): override the module-level `ROOT_PATH`. Type: string. Default: not provided → `ROOT_PATH` keeps its hardcoded value (`./Input/SBC Paper/`). When provided, `ROOT_PATH` is set to the supplied value and becomes the basis for deriving file paths described below.

- `--pdf-file <path>` (optional): explicitly set `PDF_FILE`. Type: string. Default behavior:
  - If `--pdf-file` is provided, its value becomes `PDF_FILE` (takes precedence).
  - If `--pdf-file` is not provided and `--root-path` is provided, `PDF_FILE` is derived as `f"{ROOT_PATH}main.pdf"` using the (possibly overridden) `ROOT_PATH`.
  - If neither `--pdf-file` nor `--root-path` is provided, `PDF_FILE` keeps the hardcoded default from the source (initially `f"{ROOT_PATH}main.pdf"`).

- `--bibtex-file <path>` (optional): explicitly set `BIBTEX_FILE`. Type: string. Default behavior mirrors `--pdf-file` logic:
  - Explicit `--bibtex-file` value takes precedence.
  - If not provided and `--root-path` is provided, `BIBTEX_FILE` is derived as `f"{ROOT_PATH}main.bib"`.
  - If neither provided, `BIBTEX_FILE` keeps its hardcoded default.

- `--glossary-file <path>` (optional): explicitly set `GLOSSARY_FILE`. Type: string. Default behavior mirrors `--pdf-file` logic:
  - Explicit `--glossary-file` value takes precedence.
  - If not provided and `--root-path` is provided, `GLOSSARY_FILE` is derived as `f"{ROOT_PATH}entradas-siglas.tex"`.
  - If neither provided, `GLOSSARY_FILE` keeps its hardcoded default.

Precedence summary (exact behavior implemented):

- Explicit file flags (`--pdf-file`, `--bibtex-file`, `--glossary-file`) override any derived values.
- When `--root-path` is provided but no explicit file flags are given, the code derives the three files from the effective `ROOT_PATH` as shown above.
- When no CLI arguments are provided the program uses the hardcoded defaults present in `main.py`.

## Results

The script writes a JSON report of findings to the path given by the `OUTPUT_REPORT` constant. With default constants the file written is:

```
./Input/SBC Paper/latex_review_report.json
```

Additional side effects performed by the implementation:

- The script may modify `.tex` files in-place under `ROOT_PATH` when an auto-fix is applied (the code writes back modified files when any fix flag is set).
- A log file is created by the repository-local `Logger` and the script redirects `sys.stdout` and `sys.stderr` to the `Logger` instance. The logger is instantiated with `"./Logs/{Path(__file__).stem}.log"`, which with the provided filename results in `./Logs/main.log`.
- The script registers a sound-playing callback via `atexit.register(play_sound)` when `RUN_FUNCTIONS["Play Sound"]` is truthy; the `play_sound` function performs no action on Windows (it returns immediately) and otherwise attempts to run an OS-specific playback command if `SOUND_FILE` exists.

## How to Cite?

If you use the LaTeX-Reviewer in your research, please cite it using the following BibTeX entry:

```
@misc{softwareLaTeX-Reviewer:2026,
  title = {LaTeX-Reviewer: Automated reviewer for academic LaTeX projects that detects common writing, formatting, and style issues and applies safe, deterministic auto-fixes where unambiguous. Produces a structured JSON report of findings and changes to support CI integration and reproducible proofreading.},
  author = {Breno Farias da Silva},
  year = {2026},
  howpublished = {https://github.com/BrenoFariasdaSilva/LaTeX-Reviewer},
  note = {Accessed on February 23, 2026}
}
```

Additionally, a `main.bib` file is available in the root directory of this repository, in which contains the BibTeX entry for this project.

If you find this repository valuable, please don't forget to give it a ⭐ to show your support! Contributions are highly encouraged, whether by creating issues for feedback or submitting pull requests (PRs) to improve the project. For details on how to contribute, please refer to the [Contributing](#contributing) section below.

Thank you for your support and for recognizing the contribution of this tool to your work!

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. If you have suggestions for improving the code, your insights will be highly welcome.
In order to contribute to this project, please follow the guidelines below or read the [CONTRIBUTING.md](CONTRIBUTING.md) file for more details on how to contribute to this project, as it contains information about the commit standards and the entire pull request process.
Please follow these guidelines to make your contributions smooth and effective:

1. **Set Up Your Environment**: Ensure you've followed the setup instructions in the [Setup](#setup) section to prepare your development environment.

2. **Make Your Changes**:
   - **Create a Branch**: `git checkout -b feature/YourFeatureName`
   - **Implement Your Changes**: Make sure to test your changes thoroughly.
   - **Commit Your Changes**: Use clear commit messages, for example:
     - For new features: `git commit -m "FEAT: Add some AmazingFeature"`
     - For bug fixes: `git commit -m "FIX: Resolve Issue #123"`
     - For documentation: `git commit -m "DOCS: Update README with new instructions"`
     - For refactorings: `git commit -m "REFACTOR: Enhance component for better aspect"`
     - For snapshots: `git commit -m "SNAPSHOT: Temporary commit to save the current state for later reference"`
   - See more about crafting commit messages in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

3. **Submit Your Contribution**:
   - **Push Your Changes**: `git push origin feature/YourFeatureName`
   - **Open a Pull Request (PR)**: Navigate to the repository on GitHub and open a PR with a detailed description of your changes.

4. **Stay Engaged**: Respond to any feedback from the project maintainers and make necessary adjustments to your PR.

5. **Celebrate**: Once your PR is merged, celebrate your contribution to the project!

## Collaborators

We thank the following people who contributed to this project:

<table>
  <tr>
    <td align="center">
      <a href="#" title="defina o titulo do link">
        <img src="https://github.com/BrenoFariasdaSilva.png" width="100px;" alt="My Profile Picture"/><br>
        <sub>
          <b>Breno Farias da Silva</b>
        </sub>
      </a>
    </td>
  </tr>
</table>

## License

### Apache License 2.0

This project is licensed under the [Apache License 2.0](LICENSE). This license permits use, modification, distribution, and sublicense of the code for both private and commercial purposes, provided that the original copyright notice and a disclaimer of warranty are included in all copies or substantial portions of the software. It also requires a clear attribution back to the original author(s) of the repository. For more details, see the [LICENSE](LICENSE) file in this repository.
