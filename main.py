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
