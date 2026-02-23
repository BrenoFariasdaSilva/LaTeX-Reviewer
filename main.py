r"""
================================================================================
Python LaTeX Review
================================================================================
Author      : Breno Farias da Silva
Created     : 2026-02-23
Description :
    Automatically detects and fixes common LaTeX writing and formatting issues
    in academic papers. The script operates directly on LaTeX source files,
    preserving formatting, indentation, and comments, while producing a
    machine-readable JSON review report.

    The tool is designed to reduce manual proofreading effort and to be safely
    integrated into CI and automated review pipelines.

    Key features include:
        - Automatic detection of common LaTeX writing and formatting issues
        - Safe, deterministic, and repeatable auto-fix operations
        - Comment-aware parsing that never uncomments content
        - Preservation of spacing, indentation, and tabs
        - Generation of a structured JSON review report

Usage:
    1. Configure the ROOT_PATH and OUTPUT_REPORT variables if needed.
    2. Execute the script via Makefile or directly with Python.
        $ python latex_review_tool.py
    3. Review the generated JSON report for detected issues and applied fixes.

Outputs:
    - review_report.json

TODOs:
    - Verify for used \gls{} entries against defined glossary terms.
    - Update README to include the verifications performed by the tool.
    - Add CLI argument parsing for configuration overrides.
    - Update README to include instructions for running the tool and interpreting the report.
    - Extend language support for pronoun detection.
    - Improve math-mode parsing robustness.

Dependencies:
    - Python >= 3.9
    - colorama
    - pathlib
    - json
    - re

Assumptions & Notes:
    - Only .tex files are processed.
    - Files are assumed to be UTF-8 encoded.
    - The script does not attempt to fully parse LaTeX; it relies on safe,
        conservative heuristics.
    - Auto-fixes are applied only when unambiguous and safe.
"""


import atexit  # For playing a sound when the program finishes
import datetime  # For getting the current date and time
import json  # For generating the JSON report
import os  # For filesystem operations
import platform  # For getting the operating system name
import re  # For pattern matching
import sys  # For system-specific parameters and functions
from colorama import Style  # For coloring the terminal
from Logger import Logger  # For logging output to both terminal and file
from pathlib import Path  # For handling file paths
from functools import partial  # For binding replacement functions in regex
from spellchecker import SpellChecker  # For spell checking


# Macros:
class BackgroundColors:  # Colors for the terminal
    CYAN = "\033[96m"  # Cyan
    GREEN = "\033[92m"  # Green
    YELLOW = "\033[93m"  # Yellow
    RED = "\033[91m"  # Red
    BOLD = "\033[1m"  # Bold
    UNDERLINE = "\033[4m"  # Underline
    CLEAR_TERMINAL = "\033[H\033[J"  # Clear the terminal


# Execution Constants:
VERBOSE = False  # Set to True to output verbose messages


# File Paths:
ROOT_PATH = f"./Input/SBC Paper/"  # Root directory of the LaTeX project
PDF_FILE = f"{ROOT_PATH}main.pdf"  # Compiled PDF used for rendered-output verifications
BIBTEX_FILE = f"{ROOT_PATH}main.bib"  # Compiled PDF used for rendered-output verifications
OUTPUT_REPORT = f"{ROOT_PATH}latex_review_report.json"  # JSON report output path


# Regex Patterns:
PRONOUNS = {
    "en": [
        r"\bI(?=\b|')",
        r"\bme(?=\b|')",
        r"\bmy(?=\b|')",
        r"\bmine(?=\b|')",
        r"\bmyself\b",
        r"\bwe(?=\b|')",
        r"\bus(?=\b|')",
        r"\bour(?=\b|')",
        r"\bours(?=\b|')",
        r"\bourselves\b",
    ],
    "pt-br": [
        r"\beu\b",
        r"\bmim\b",
        r"\bme\b",
        r"\bmeu\b",
        r"\bminha\b",
        r"\bmeus\b",
        r"\bminhas\b",
        r"\bnós\b",
        r"\bnos\b",
        r"\bnossa\b",
        r"\bnosso\b",
        r"\bnossas\b",
        r"\bnossos\b",
    ],
}


# Safe Spell Fixes:
SAFE_SPELL_FIXES = {
    "futhermore": "furthermore",
    "seperate": "separate",
    "occured": "occurred",
    "teh": "the",
    "recieve": "receive",
}


# Logger Setup:
logger = Logger(f"./Logs/{Path(__file__).stem}.log", clean=True)  # Create a Logger instance
sys.stdout = logger  # Redirect stdout to the logger
sys.stderr = logger  # Redirect stderr to the logger


# Sound Constants:
SOUND_COMMANDS = {
    "Darwin": "afplay",
    "Linux": "aplay",
    "Windows": "start",
}  # The commands to play a sound for each operating system
SOUND_FILE = "./.assets/Sounds/NotificationSound.wav"  # The path to the sound file


# RUN_FUNCTIONS:
RUN_FUNCTIONS = {
    "Play Sound": True,  # Set to True to play a sound when the program finishes
}


# Functions Definitions:


def verbose_output(true_string="", false_string=""):
    """
    Outputs a message if the VERBOSE constant is set to True.

    :param true_string: The string to be outputted if the VERBOSE constant is set to True.
    :param false_string: The string to be outputted if the VERBOSE constant is set to False.
    :return: None
    """

    if VERBOSE and true_string != "":  # If VERBOSE is True and a true_string was provided
        print(true_string)  # Output the true statement string
    elif false_string != "":  # If a false_string was provided
        print(false_string)  # Output the false statement string


def verify_filepath_exists(filepath):
    """
    Verify if a file or folder exists at the specified path.

    :param filepath: Path to the file or folder
    :return: True if the file or folder exists, False otherwise
    """

    verbose_output(
        f"{BackgroundColors.GREEN}Verifying if the file or folder exists at the path: {BackgroundColors.CYAN}{filepath}{Style.RESET_ALL}"
    )  # Output the verbose message

    return os.path.exists(filepath)  # Return True if the file or folder exists, False otherwise


def initialize_report():
    """
    Initialize the review report structure.

    :return: Dictionary representing the empty report
    """

    return {
        "unresolved_references": [],
        "repeated_left_parentheses": [],
        "repeated_right_parentheses": [],
        "pronouns": [],
        "apostrophes": [],
        "decimal_formatting": [],
        "decimal_precision": [],
        "double_whitespace": [],
        "glossary_plural": [],
        "underscore_misuse": [],
        "percentage_misuse": [],
        "missing_section_label": [],
        "missing_bib_entries": [],
        "numeric_representation": [],
        "itemize_punctuation": [],
        "duplicate_citations": [],
        "spelling": [],
    }  # Return initialized empty report structure


def replacement_preserve_case(m, right):
    """
    Replacement function for regex that preserves the case of the original word.

    :param m: regex match object
    :param right: replacement string to use
    :return: replacement string with preserved case
    """

    orig = m.group(0)  # Original matched token

    if orig.isupper():  # If the original is all uppercase, return the replacement in uppercase
        return right.upper()  # Preserve all-uppercase

    if orig[0].isupper():  # If the original is capitalized, return the replacement capitalized
        return right.capitalize()  # Preserve initial capitalization

    return right  # Default lowercase replacement


def replace_safe(s: str):
    """
    Apply safe, case-preserving replacements from SAFE_SPELL_FIXES to a string.

    :param s: Input string to process
    :return: Transformed string with safe replacements applied
    """

    out = s  # Working copy of the input string

    for wrong, right in SAFE_SPELL_FIXES.items():  # Iterate configured safe fixes
        out = re.sub(
            rf"\b{re.escape(wrong)}\b",
            partial(replacement_preserve_case, right=right),
            out,
            flags=re.IGNORECASE,
        )  # Apply replacement with case-preserving helper bound to `right`
    return out  # Return transformed string


def split_code_and_comment(line):
    """
    Split a LaTeX line into code and comment parts.

    :param line: The original line from the file
    :return: Tuple (code_part, comment)
    """

    if "%" in line:  # Split off LaTeX comments — do not touch commented text
        code_part, comment_part = line.split("%", 1)  # Separate code and comment sections
        comment = "%" + comment_part  # Preserve comment with leading '%'
    else:
        code_part = line  # No inline comment present
        comment = ""  # Empty comment string
    return code_part, comment  # Return code and comment parts


def apply_safe_replacements(filepath, line_number, report, code_part, original_line):
    """
    Apply safe replacements from SAFE_SPELL_FIXES and record the change in report.

    :param filepath: Path to the .tex file
    :param line_number: Line number where replacement occurred
    :param report: Report dictionary to append to
    :param code_part: The code portion of the line (no comment)
    :param original_line: The original full line for context
    :return: Tuple (possibly modified code_part, modified_flag)
    """

    new_code = replace_safe(code_part)  # Apply safe replacements to code part
    if new_code != code_part:  # If replacements changed the code part
        report["spelling"].append(  # Recorded safe spelling replacement
            {
                "file": str(filepath),  # File where replacement occurred
                "line": line_number,  # Line number where replacement occurred
                "before": code_part.rstrip("\n"),  # Original code part before change
                "after": new_code.rstrip("\n"),  # New code part after change
                "context": original_line.strip(),  # Full line context
                "auto_fixable": True,  # Mark as auto-fixable
                "applied_fix": True,  # Mark as applied
            }
        )  # End append
        code_part = new_code  # Update code part with applied safe fixes
        return code_part, True  # Return modified code and flag
    return code_part, False  # Return original code and False when unchanged


def is_ignored_by_safe_spell_fixes(lw):
    """
    Return True when the lowercased word is present in SAFE_SPELL_FIXES.

    :param lw: Lowercased word to check
    :return: True if word is in SAFE_SPELL_FIXES
    """

    return lw in SAFE_SPELL_FIXES  # Membership check against SAFE_SPELL_FIXES


def get_spell_suggestion_safe(spell, lw):
    """
    Safely query the SpellChecker for a suggestion; return suggestion or None.

    :param spell: SpellChecker instance
    :param lw: Lowercased word to query
    :return: Suggestion string or None
    """

    try:  # Protect against spellchecker errors
        if lw not in spell:  # If word is not found in dictionary
            suggestion = spell.correction(lw)  # Ask spellchecker for a suggestion
            return suggestion  # Return suggestion (may be None)
        return None  # Return None when word exists in dictionary
    except Exception:  # On any error from spellchecker
        return None  # Return None to mimic original exception swallowing


def append_spell_suggestion(report, filepath, line_number, word, suggestion, original_line):
    """
    Append a suggestion entry into the report['spelling'] list.

    :param report: Report dictionary
    :param filepath: Path to file where suggestion was found
    :param line_number: Line number for suggestion
    :param word: Original word
    :param suggestion: Suggested correction
    :param original_line: Full original line for context
    :return: None
    """

    report["spelling"].append(  # Append suggestion entry to report
        {
            "file": str(filepath),  # File path where suggestion occurred
            "line": line_number,  # Line number for suggestion
            "word": word,  # Original word
            "suggestion": suggestion,  # Suggested correction
            "context": original_line.strip(),  # Full line context
            "auto_fixable": False,  # Suggestion is not auto-fixable
        }
    )  # End append


def add_spell_suggestions(filepath, line_number, report, code_part, spell, original_line):
    """
    Use a SpellChecker to add suggestions to the report for unknown words.

    :param filepath: Path to the .tex file
    :param line_number: Line number where suggestions are generated
    :param report: Report dictionary to append suggestions to
    :param code_part: The code portion of the line (no comment)
    :param spell: SpellChecker instance
    :param original_line: The original full line for context
    :return: None
    """

    for m in re.finditer(r"(?<!\\)\b([A-Za-z][A-Za-z']+)\b", code_part):  # Iterate candidate words (skip LaTeX commands and math)
        word = m.group(1)  # Extract matched word
        lw = word.lower()  # Lowercased word for verifications
        
        if is_ignored_by_safe_spell_fixes(lw):  # Skip words we already fix safely
            continue  # Continue to next word
        
        suggestion = get_spell_suggestion_safe(spell, lw)  # Query spellchecker safely
        
        if suggestion and suggestion.lower() != lw:  # If suggestion differs
            append_spell_suggestion(report, filepath, line_number, word, suggestion, original_line)  # Add suggestion entry to report


def detect_and_fix_spelling(filepath, line, line_number, report, spell=None):
    """
    Apply safe deterministic fixes from SAFE_SPELL_FIXES and, if `spell`
    (a SpellChecker) is provided, add suggestions (no automatic changes).

    Returns: (possibly_modified_line, modified_flag)
    """
    
    code_part, comment = split_code_and_comment(line)  # Split code and comment parts

    modified = False  # Track whether automatic safe fixes were applied

    code_part, was_modified = apply_safe_replacements(filepath, line_number, report, code_part, line)  # Apply safe replacements and record
    modified = modified or was_modified  # Update modified flag if safe replacements applied

    if spell is not None:  # If a spellchecker is available, add suggestions (do not auto-fix)
        add_spell_suggestions(filepath, line_number, report, code_part, spell, line)  # Add suggestions to report

    return code_part + comment, modified  # Return possibly modified line and whether we changed it


def detect_apostrophes(filepath, line, line_number, report):
    """
    Detect improper apostrophe usage.

    :param filepath: Path to the .tex file
    :param line: Line content
    :param line_number: Line number
    :param report: Dictionary accumulating the report data
    :return: None
    """

    if "'" in line and not ("``" in line or "''" in line):  # If there are apostrophes in the line not part of quotes
        report["apostrophes"].append(  # Record apostrophe occurrence
            {
                "file": str(filepath),
                "line": line_number,
                "matched_text": line.strip(),
                "auto_fixable": False,
            }
        )  # End append


def extract_decimals_from_line(line):
    """
    Extract decimal numbers from a line using configured regex.

    :param line: Line content
    :return: List of decimal strings found
    """

    decimal_pattern = re.compile(r"\b\d+[.,]\d+\b")  # Match decimal numbers using dot or comma: 1.23 | 10,5 | 0.75
    decimals = decimal_pattern.findall(line)  # Find all decimal numbers in the line
    return decimals  # Return list of decimals found


def append_decimal_reports(filepath, line_number, report, number):
    """
    Append decimal formatting and precision entries for a single numeric token.

    :param filepath: Path to the .tex file
    :param line_number: Line number where the number was found
    :param report: Report dictionary to append entries to
    :param number: The numeric string token to analyze
    :return: None
    """

    separator = "." if "." in number else ","  # Identify decimal separator used
    precision = len(number.split(separator)[1])  # Count decimal places for precision

    report["decimal_formatting"].append(  # Append decimal formatting info
        {
            "file": str(filepath),  # File where the number was found
            "line": line_number,  # Line number where the number was found
            "value": number,  # The numeric token value
            "separator": separator,  # The separator used in the token
            "auto_fixable": False,  # Not auto-fixable
        }
    )  # End append

    report["decimal_precision"].append(  # Append decimal precision info
        {
            "file": str(filepath),  # File where the number was found
            "line": line_number,  # Line number where the number was found
            "value": number,  # The numeric token value
            "precision": precision,  # Number of decimal places
            "auto_fixable": False,  # Not auto-fixable
        }
    )  # End append


def find_percentages_and_proportions(line):
    """
    Find percentage and proportion patterns in a line.

    :param line: Line content
    :return: Tuple (percentages, proportions)
    """

    percentage_pattern = re.compile(r"\b\d+\s*\\%")  # Match percentages written correctly as: 25 \%
    percentages = percentage_pattern.findall(line)  # Find percentage values

    proportion_pattern = re.compile(r"\b0[.,]\d+\b")  # Match proportions written as decimals: 0.25 | 0,75
    proportions = proportion_pattern.findall(line)  # Find decimal proportions
    return percentages, proportions  # Return both lists


def append_mixed_numeric_representation(report, filepath, line_number):
    """
    Append a mixed numeric representation issue entry into the report.

    :param report: Report dictionary
    :param filepath: Path to the .tex file
    :param line_number: Line number where issue was detected
    :return: None
    """

    report["numeric_representation"].append(  # Record mixed numeric representation issue
        {
            "file": str(filepath),  # File path where issue occurred
            "line": line_number,  # Line number where issue occurred
            "issue": "mixed_decimal_and_percentage",  # Issue identifier
            "auto_fixable": False,  # Not auto-fixable
        }
    )  # End append


def detect_numeric_consistency(filepath, line, line_number, report):
    """
    Detect numeric usage consistency.

    Verifies for:
    - Decimal separator usage (dot vs comma)
    - Decimal precision consistency
    - Mixed usage of decimals and percentages
    - Mapping of numeric representations for later global analysis

    :param filepath: Path to the .tex file
    :param line: Line content
    :param line_number: Line number
    :param report: Dictionary accumulating the report data
    :return: None
    """

    if re.match(r"\s*%", line):  # Ignore fully commented lines
        return  # Skip analysis safely

    decimals = extract_decimals_from_line(line)  # Find decimal numbers in the line

    for number in decimals:  # Iterate through each decimal number found
        append_decimal_reports(filepath, line_number, report, number)  # Append formatting and precision entries for this number

    percentages, proportions = find_percentages_and_proportions(line)  # Detect percentages and proportions in the line

    if percentages and proportions:  # If both representations are used in the same line
        append_mixed_numeric_representation(report, filepath, line_number)  # Record mixed numeric representation issue


def is_begin_itemize_line(line):
    """
    Return True if the provided line marks the beginning of an itemize environment.

    :param line: Line content to check
    :return: True if line contains a begin{itemize}
    """

    pattern = re.compile(r"^(\s*)%?\s*\\begin\{itemize\}")  # Regex for begin{itemize}
    return bool(pattern.search(line))  # Return whether a begin{itemize} was found


def is_end_itemize_line(line):
    """
    Return True if the provided line marks the end of an itemize environment.

    :param line: Line content to check
    :return: True if line contains an end{itemize}
    """

    pattern = re.compile(r"^(\s*)%?\s*\\end\{itemize\}")  # Regex for end{itemize}
    return bool(pattern.search(line))  # Return whether an end{itemize} was found


def process_item_lines_and_update(lines, item_lines, filepath, report):
    r"""
    Process collected \item lines: normalize punctuation, update lines in-place, and append report.

    :param lines: List of file lines to modify
    :param item_lines: List of indices of \item lines collected within the environment
    :param filepath: Path to the .tex file being processed
    :param report: Report dictionary to append entries to
    :return: True if any line was modified, False otherwise
    """

    ITEM_PATTERN = re.compile(r"^(\s*)(%?\s*\\item\s+)(.*?)(\s*)$")  # Pattern to parse \item lines
    modified = False  # Track whether any modifications occurred
    
    for idx, line_no in enumerate(item_lines):  # Iterate collected \item line indices
        original = lines[line_no].rstrip("\n")  # Get the original line content
        match = ITEM_PATTERN.match(original)  # Match the \item line
        
        if not match:  # If the line does not match the \item pattern
            continue  # Skip to the next line

        indent, prefix, content, trailing = match.groups()  # Extract groups

        content = re.sub(r"[.;]\s*$", "", content)  # Remove existing punctuation

        if idx < len(item_lines) - 1:  # Last item ends with ".", others with ";"
            content += ";"  # Add semicolon
        else:  # Last item ends with a period
            content += "."  # Add period

        new_line = f"{indent}{prefix}{content}{trailing}\n"  # Reconstruct the line

        if new_line != lines[line_no]:  # If the line was modified
            lines[line_no] = new_line  # Update the line in the list
            modified = True  # Set the modified flag to True

    if item_lines:  # If any \item lines were collected
        report["itemize_punctuation"].append(  # Record that itemize punctuation was fixed
            {
                "file": str(filepath),  # File where fix was applied
                "auto_fixable": True,  # Mark as auto-fixable
                "applied_fix": True,  # Mark as applied
            }
        )  # End append

    return modified  # Return whether any modification occurred


def is_table_like_environment_line(line):
    """
    Return True if the provided line is a table-like begin/end environment.

    :param line: Line content to check
    :return: True if line contains a begin/end of tabular/table/longtable
    """

    if re.search(r"\\begin\{(tabular|table|longtable)\}", line) or re.search(r"\\end\{(tabular|table|longtable)\}", line):  # Detect table-like begin/end
        return True  # Return True when table-like environment detected
    return False  # Return False when not detected


def get_leading_whitespace_match(line):
    """
    Return a regex match for leading whitespace and the remainder of the line.

    :param line: Line content to check
    :return: Regex Match object or None
    """

    return re.match(r"^([ \t]*)(.*)$", line)  # Match leading whitespace and content


def process_double_whitespace_and_report(filepath, line_number, report, indent, content, original_line):
    """
    Process content for multiple consecutive spaces, update report and return new line.

    :param filepath: Path to the .tex file
    :param line_number: Line number where content was found
    :param report: Report dictionary to append entries to
    :param indent: Leading indentation string
    :param content: Content part of the line without indentation
    :param original_line: The original full line for context
    :return: Tuple (new_line or None, modified_flag)
    """

    if re.search(r"[^ \t]  +", content):  # If there are multiple consecutive spaces in the content
        fixed_content = re.sub(r" {2,}", " ", content)  # Replace multiple spaces with a single space
        if fixed_content != content:  # If the content was modified
            new_line = indent + fixed_content  # Reconstruct the line with original indentation
            report["double_whitespace"].append(  # Append double-whitespace fix to report
                {
                    "file": str(filepath),  # File where fix was applied
                    "line": line_number,  # Line number where fix was applied
                    "before": original_line.rstrip("\n"),  # Original line before change
                    "after": new_line.rstrip("\n"),  # New line after change
                    "auto_fixable": True,  # Mark as auto-fixable
                    "applied_fix": True,  # Mark as applied
                }
            )  # End append
            return new_line, True  # Return the modified line and True

    return None, False  # Return None and False when unchanged


def fix_itemize_punctuation(filepath, lines, report):
    """
    Fix punctuation consistency inside itemize environments.

    Rules:
    - Every \\item ends with ';'
    - Last \\item ends with '.'
    - Works with commented itemize environments
    - Preserves indentation, spacing, and comment markers

    :param filepath: Path to the .tex file
    :param lines: List of file lines
    :param report: Dictionary accumulating the report data
    :return: Tuple (possibly modified lines, modification flag)
    """

    ITEM_PATTERN = re.compile(r"^(\s*)(%?\s*\\item\s+)(.*?)(\s*)$")  # Match any \item, commented or not

    in_itemize = False  # Flag indicating if we are inside an itemize environment
    item_lines = []  # List of line indices for \item lines
    modified = False  # Flag to track if any modifications were made

    for i, line in enumerate(lines):  # Iterate through each line
        if is_begin_itemize_line(line):  # Detect begin{itemize}, commented or not
            in_itemize = True  # Set the flag to True
            item_lines = []  # Reset the list of \item line indices
            continue  # Continue to the next line

        if is_end_itemize_line(line) and in_itemize:  # Detect end{itemize}, commented or not
            was_modified = process_item_lines_and_update(lines, item_lines, filepath, report)  # Process collected \item lines
            if was_modified:  # If processing modified any lines
                modified = True  # Set the modified flag to True

            in_itemize = False  # Reset the flag
            continue  # Continue to the next line

        if in_itemize and ITEM_PATTERN.match(line):  # If inside itemize and line matches \item
            item_lines.append(i)  # Collect the line index

    return lines, modified  # Return the (possibly modified) lines and modification flag


def fix_double_whitespace(filepath, line, line_number, report):
    """
    Fix multiple consecutive spaces in running text.

    - Preserves leading indentation
    - Skips table-like environments

    :param filepath: Path to the .tex file
    :param line: Line content
    :param line_number: Line number
    :param report: Dictionary accumulating the report data
    :return: Tuple (possibly modified line, modification flag)
    """

    if is_table_like_environment_line(line):  # Skip table-like environments
        return line, False  # Return the original line and False

    match = get_leading_whitespace_match(line)  # Match leading whitespace and content
    if not match:  # Safety guard (required for static analysis and robustness)
        return line, False  # Return the original line and False

    indent, content = match.groups()  # Extract indentation and content

    new_line, was_modified = process_double_whitespace_and_report(filepath, line_number, report, indent, content, line)  # Process and possibly update
    if was_modified:  # If processing modified the line
        return new_line, True  # Return the modified line and True

    return line, False  # Return the original line and False


def fix_glossary_plural(filepath, line, line_number, report):
    """
    Fix invalid plural usage of \\gls{} commands.

    :param filepath: Path to the .tex file
    :param line: Line content
    :param line_number: Line number
    :param report: Dictionary accumulating the report data
    :return: Tuple (possibly modified line, modification flag)
    """

    if r"\gls{" in line and re.search(r"\\gls\{[^}]+\}s", line):  # If there is a glossary plural misuse in the line
        new_line = re.sub(r"\\gls\{([^}]+)\}s", r"\\glspl{\1}", line)  # Fix the glossary plural misuse
        if new_line != line:  # If the line was modified
            report["glossary_plural"].append(  # Append glossary plural fix to report
                {
                    "file": str(filepath),
                    "line": line_number,
                    "before": line.rstrip("\n"),
                    "after": new_line.rstrip("\n"),
                    "auto_fixable": True,
                    "applied_fix": True,
                }
            )  # End append
            return new_line, True  # Return the modified line and True

    return line, False  # Return the original line and False


def fix_underscore_misuse(filepath, line, line_number, report):
    """
    Fix unescaped underscores outside math mode.

    :param filepath: Path to the .tex file
    :param line: Line content
    :param line_number: Line number
    :param report: Dictionary accumulating the report data
    :return: Tuple (possibly modified line, modification flag)
    """

    if "_" in line and not re.search(r"\\_", line):  # If there are unescaped underscores in the line
        new_line = line.replace("_", r"\_")  # Escape the underscores
        if new_line != line:  # If the line was modified
            report["underscore_misuse"].append(  # Append underscore fix to report
                {
                    "file": str(filepath),
                    "line": line_number,
                    "before": line.rstrip("\n"),
                    "after": new_line.rstrip("\n"),
                    "auto_fixable": True,
                    "applied_fix": True,
                }
            )  # End append
            return new_line, True  # Return the modified line and True

    return line, False  # Return the original line and False


def fix_percentage_misuse(filepath, line, line_number, report):
    """
    Fix percentage usage consistency.

    Rules:
    - Percentages must be written as ' <number> \\%'
    - A space is required before '\\%'
    - Ignore fully commented lines

    :param filepath: Path to the .tex file
    :param line: Line content
    :param line_number: Line number
    :param report: Dictionary accumulating the report data
    :return: Tuple (possibly modified line, modification flag)
    """

    if re.match(r"\s*%", line):  # Ignore fully commented lines
        return line, False  # Return the

    original_line = line  # Store the original line

    line = re.sub(r"(\d)%", r"\1 \\%", line)  # Fix missing backslash before percent: 10% -> 10 \%

    line = re.sub(r"(\d)\\%", r"\1 \\%", line)  # Ensure space before \%: 10\% -> 10 \%

    if line != original_line:  # If the line was modified
        report["percentage_misuse"].append(  # Append percentage fix to report
            {
                "file": str(filepath),
                "line": line_number,
                "before": original_line.rstrip("\n"),
                "after": line.rstrip("\n"),
                "auto_fixable": True,
                "applied_fix": True,
            }
        )  # End append
        return line, True  # Return the modified line and True

    return line, False  # Return the original line and False


def analyze_line(filepath, line, line_number, report, bib_keys=None, spell=None):
    """
    Analyze a single line of a LaTeX file.

    :param filepath: Path to the .tex file
    :param line: Current line content
    :param line_number: Line number in the file
    :param report: Dictionary accumulating the report data
    :return: Tuple (possibly modified line, modification flag)
    """

    modified = False  # Flag to track if the line was modified

    detect_unresolved_references(filepath, line, line_number, report)  # Detect unresolved references
    detect_repeated_parentheses(filepath, line, line_number, report)  # Detect repeated parentheses
    detect_pronouns(filepath, line, line_number, report)  # Detect first-person pronouns
    detect_apostrophes(filepath, line, line_number, report)  # Detect improper apostrophe usage
    detect_numeric_consistency(filepath, line, line_number, report)  # Detect numeric consistency issues

    if bib_keys is not None:  # If BibTeX keys are provided
        detect_missing_bib_entries(filepath, line, line_number, bib_keys, report)  # Detect missing BibTeX entries

    line, dup_cite_modified = fix_duplicate_citations(filepath, line, line_number, report)  # Fix duplicate keys in \cite
    modified = modified or dup_cite_modified  # Update modified flag if duplicates fixed

    line, spelling_modified = detect_and_fix_spelling(filepath, line, line_number, report, spell)  # Detect and fix spelling
    modified = modified or spelling_modified  # Update modified flag if spelling changed

    line, double_whitespace_modified = fix_double_whitespace(filepath, line, line_number, report)  # Fix multiple consecutive spaces
    modified = modified or double_whitespace_modified  # Update modification flag

    line, glossary_modified = fix_glossary_plural(filepath, line, line_number, report)  # Fix glossary plural misuse
    modified = modified or glossary_modified  # Update modification flag

    line, underscore_modified = fix_underscore_misuse(filepath, line, line_number, report)  # Fix underscore misuse
    modified = modified or underscore_modified  # Update modification flag

    line, percentage_modified = fix_percentage_misuse(filepath, line, line_number, report)  # Fix percentage misuse
    modified = modified or percentage_modified  # Update modification flag

    return line, modified  # Return the (possibly modified) line and modification flag


def analyze_file(filepath, report, bib_keys=None, spell=None) -> tuple[str, bool]:
    """
    Analyze a single LaTeX file and apply safe auto-fixes.

    :param filepath: Path to the .tex file
    :param report: Dictionary accumulating the report data
    :return: None
    """

    with open(filepath, "r", encoding="utf-8") as file:  # Open the file for reading
        lines = file.readlines()  # Read all lines from the file into a list

    modified = False  # Flag to track if the file was modified

    line_index = 0  # Start index for first-pass modifications
    while line_index < len(lines):  # Iterate through lines allowing insertions
        was_modified, label_inserted = fix_missing_section_labels(filepath, lines, line_index, report)  # Attempt to insert missing label
        modified = modified or was_modified  # Update file-level modified flag
        if label_inserted:  # If a label was inserted just after current line
            line_index += 2  # Skip over the newly inserted label line
        else:
            line_index += 1  # Move to next original line

    for line_number, line in enumerate(lines, start=1):  # Iterate through each line with line numbers
        line, was_modified = analyze_line(filepath, line, line_number, report, bib_keys, spell)  # Analyze a single line for issues and fixes
        modified = modified or was_modified  # Update modification flag if any fixes applied
        lines[line_number - 1] = str(line)  # Replace list entry with possibly modified line

    if modified:  # If the file was modified
        with open(filepath, "w", encoding="utf-8") as file:  # Open the file for writing
            file.writelines(lines)  # Write the modified lines back to the file
            
    return str(filepath), modified


def to_seconds(obj):
    """
    Converts various time-like objects to seconds.
    
    :param obj: The object to convert (can be int, float, timedelta, datetime, etc.)
    :return: The equivalent time in seconds as a float, or None if conversion fails
    """
    
    if obj is None:  # None can't be converted
        return None  # Signal failure to convert
    if isinstance(obj, (int, float)):  # Already numeric (seconds or timestamp)
        return float(obj)  # Return as float seconds
    if hasattr(obj, "total_seconds"):  # Timedelta-like objects
        try:  # Attempt to call total_seconds()
            return float(obj.total_seconds())  # Use the total_seconds() method
        except Exception:
            pass  # Fallthrough on error
    if hasattr(obj, "timestamp"):  # Datetime-like objects
        try:  # Attempt to call timestamp()
            return float(obj.timestamp())  # Use timestamp() to get seconds since epoch
        except Exception:
            pass  # Fallthrough on error
    return None  # Couldn't convert


def calculate_execution_time(start_time, finish_time=None):
    """
    Calculates the execution time and returns a human-readable string.

    Accepts either:
    - Two datetimes/timedeltas: `calculate_execution_time(start, finish)`
    - A single timedelta or numeric seconds: `calculate_execution_time(delta)`
    - Two numeric timestamps (seconds): `calculate_execution_time(start_s, finish_s)`

    Returns a string like "1h 2m 3s".
    """

    if finish_time is None:  # Single-argument mode: start_time already represents duration or seconds
        total_seconds = to_seconds(start_time)  # Try to convert provided value to seconds
        if total_seconds is None:  # Conversion failed
            try:  # Attempt numeric coercion
                total_seconds = float(start_time)  # Attempt numeric coercion
            except Exception:
                total_seconds = 0.0  # Fallback to zero
    else:  # Two-argument mode: Compute difference finish_time - start_time
        st = to_seconds(start_time)  # Convert start to seconds if possible
        ft = to_seconds(finish_time)  # Convert finish to seconds if possible
        if st is not None and ft is not None:  # Both converted successfully
            total_seconds = ft - st  # Direct numeric subtraction
        else:  # Fallback to other methods
            try:  # Attempt to subtract (works for datetimes/timedeltas)
                delta = finish_time - start_time  # Try subtracting (works for datetimes/timedeltas)
                total_seconds = float(delta.total_seconds())  # Get seconds from the resulting timedelta
            except Exception:  # Subtraction failed
                try:  # Final attempt: Numeric coercion
                    total_seconds = float(finish_time) - float(start_time)  # Final numeric coercion attempt
                except Exception:  # Numeric coercion failed
                    total_seconds = 0.0  # Fallback to zero on failure

    if total_seconds is None:  # Ensure a numeric value
        total_seconds = 0.0  # Default to zero
    if total_seconds < 0:  # Normalize negative durations
        total_seconds = abs(total_seconds)  # Use absolute value

    days = int(total_seconds // 86400)  # Compute full days
    hours = int((total_seconds % 86400) // 3600)  # Compute remaining hours
    minutes = int((total_seconds % 3600) // 60)  # Compute remaining minutes
    seconds = int(total_seconds % 60)  # Compute remaining seconds

    if days > 0:  # Include days when present
        return f"{days}d {hours}h {minutes}m {seconds}s"  # Return formatted days+hours+minutes+seconds
    if hours > 0:  # Include hours when present
        return f"{hours}h {minutes}m {seconds}s"  # Return formatted hours+minutes+seconds
    if minutes > 0:  # Include minutes when present
        return f"{minutes}m {seconds}s"  # Return formatted minutes+seconds
    return f"{seconds}s"  # Fallback: only seconds


def play_sound():
    """
    Plays a sound when the program finishes and skips if the operating system is Windows.

    :param: None
    :return: None
    """

    current_os = platform.system()  # Get the current operating system
    if current_os == "Windows":  # If the current operating system is Windows
        return  # Do nothing

    if verify_filepath_exists(SOUND_FILE):  # If the sound file exists
        if current_os in SOUND_COMMANDS:  # If the platform.system() is in the SOUND_COMMANDS dictionary
            os.system(f"{SOUND_COMMANDS[current_os]} {SOUND_FILE}")  # Play the sound
        else:  # If the platform.system() is not in the SOUND_COMMANDS dictionary
            print(
                f"{BackgroundColors.RED}The {BackgroundColors.CYAN}{current_os}{BackgroundColors.RED} is not in the {BackgroundColors.CYAN}SOUND_COMMANDS dictionary{BackgroundColors.RED}. Please add it!{Style.RESET_ALL}"
            )
    else:  # If the sound file does not exist
        print(
            f"{BackgroundColors.RED}Sound file {BackgroundColors.CYAN}{SOUND_FILE}{BackgroundColors.RED} not found. Make sure the file exists.{Style.RESET_ALL}"
        )


def main():
    """
    Main function.

    :param: None
    :return: None
    """

    print(
        f"{BackgroundColors.CLEAR_TERMINAL}{BackgroundColors.BOLD}{BackgroundColors.GREEN}Welcome to the {BackgroundColors.CYAN}Main Template Python{BackgroundColors.GREEN} program!{Style.RESET_ALL}",
        end="\n\n",
    )  # Output the welcome message
    start_time = datetime.datetime.now()  # Get the start time of the program

    report = initialize_report()  # Initialize the report dictionary
    analyze_pdf(report)  # First Pass: Rendered-Output verifications (PDF)
    tex_files = collect_tex_files(ROOT_PATH)  # Collect all .tex files under the root path

    bib_keys = load_bibtex_keys(BIBTEX_FILE)  # Load BibTeX keys from the .bib file
    spell = SpellChecker()  # Initialize the spell checker (this may take some time on first run due to loading dictionaries)

    for tex_file in tex_files:  # Iterate through each .tex file
        analyze_file(tex_file, report, bib_keys, spell)  # Analyze the file and update the report

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as file:  # Open the output report file for writing
        json.dump(report, file, indent=3)  # Write the report dictionary to the JSON file

    finish_time = datetime.datetime.now()  # Get the finish time of the program
    print(
        f"{BackgroundColors.GREEN}Start time: {BackgroundColors.CYAN}{start_time.strftime('%d/%m/%Y - %H:%M:%S')}\n{BackgroundColors.GREEN}Finish time: {BackgroundColors.CYAN}{finish_time.strftime('%d/%m/%Y - %H:%M:%S')}\n{BackgroundColors.GREEN}Execution time: {BackgroundColors.CYAN}{calculate_execution_time(start_time, finish_time)}{Style.RESET_ALL}"
    )  # Output the start and finish times
    print(
        f"\n{BackgroundColors.BOLD}{BackgroundColors.GREEN}Program finished.{Style.RESET_ALL}"
    )  # Output the end of the program message

    (
        atexit.register(play_sound) if RUN_FUNCTIONS["Play Sound"] else None
    )  # Register the play_sound function to be called when the program finishes


if __name__ == "__main__":
    """
    This is the standard boilerplate that calls the main() function.

    :return: None
    """

    main()  # Call the main function
