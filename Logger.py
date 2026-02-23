r"""
================================================================================
Logger Utility Module
================================================================================
Author      : Breno Farias da Silva
Created     : 2025-12-11
Description :
   This module implements a dual-channel logging system designed to capture
   all console output produced by Python scripts while preserving ANSI colors
   in the terminal and removing them from the log file.

   It provides consistent, color-safe logging across interactive terminals,
   background executions, CI pipelines, Makefile pipelines, and nohup/systemd
   environments.

   Key features include:
      - Automatic ANSI color stripping for log files
      - Full compatibility with interactive and non-interactive terminals
      - Mirrored output: terminal (colored) + log file (clean)
      - Optional integration by assigning it to sys.stdout/sys.stderr

Usage:
   1. Create a Logger instance:

         from logger import Logger
         logger = Logger("./Logs/output.log", clean=True)

   2. (Optional) Redirect all stdout/stderr to the logger:

         sys.stdout = logger
         sys.stderr = logger

   3. Print normally:

         print("\x1b[92mHello World\x1b[0m")

      Terminal shows colored output.
      Log file receives the same text without ANSI escape sequences.

Outputs:
   - <path>.log file with fully sanitized (color-free) log output
   - Real-time terminal output with correct ANSI handling

TODOs:
   - Timestamp prefixing for each log line
   - File rotation or size-based log splitting
   - CLI flag to force color on/off
   - Optional JSON-structured logs

Dependencies:
   - Python >= 3.8
   - colorama (optional but recommended for Windows)

Assumptions & Notes:
   - ANSI escape sequences follow the regex: \x1B\[[0-9;]*[a-zA-Z]
   - Log file always stores clean output
   - When stdout is not a TTY, color output is automatically disabled
"""

import os  # For interacting with the filesystem
import re  # For stripping ANSI escape sequences
import sys  # For replacing stdout/stderr

# Regex Constants:
ANSI_ESCAPE_REGEX = re.compile(r"\x1B\[[0-9;]*[a-zA-Z]")  # Pattern to remove ANSI colors

# Classes Definitions:


class Logger:
    """
    Simple logger class that prints colored messages to the terminal and
    writes a cleaned (ANSI-stripped) version to a log file.

    Usage:
       logger = Logger("./Logs/output.log", clean=True)
       logger.info("\x1b[92mHello world\x1b[0m")

    :param logfile_path: Path to the log file.
    :param clean: If True, truncate the log file on init; otherwise append.
    """

    def __init__(self, logfile_path, clean=False):
        """
        Initialize the Logger.

        :param self: Instance of the Logger class.
        :param logfile_path: Path to the log file.
        :param clean: If True, truncate the log file on init; otherwise append.
        """

        self.logfile_path = logfile_path  # Store log file path

        parent = os.path.dirname(logfile_path)  # Ensure log directory exists
        if parent and not os.path.exists(parent):  # Create parent directories if needed
            os.makedirs(parent, exist_ok=True)  # Safe creation

        mode = "w" if clean else "a"  # Choose file mode based on 'clean' flag
        self.logfile = open(logfile_path, mode, encoding="utf-8")  # Open log file
        self.is_tty = sys.stdout.isatty()  # Verify if stdout is a TTY

    def write(self, message):
        """
        Internal method to write messages to both terminal and log file.

        :param self: Instance of the Logger class.
        :param message: The message to log.
        """

        if message is None:  # Ignore None messages
            return  # Early exit

        out = str(message)  # Convert message to string
        if not out.endswith("\n"):  # Ensure newline termination
            out += "\n"  # Append newline if missing

        clean_out = ANSI_ESCAPE_REGEX.sub("", out)  # Strip ANSI sequences for log file

        try:  # Write to log file
            self.logfile.write(clean_out)  # Write cleaned message
            self.logfile.flush()  # Ensure immediate write
        except Exception:  # Fail silently to avoid breaking user code
            pass  # Silent fail

        try:  # Write to terminal: colored when TTY, cleaned otherwise
            if self.is_tty:  # Terminal supports colors
                sys.__stdout__.write(out)  # Write colored message
                sys.__stdout__.flush()  # Flush immediately
            else:  # Terminal does not support colors
                sys.__stdout__.write(clean_out)  # Write cleaned message
                sys.__stdout__.flush()  # Flush immediately
        except Exception:  # Fail silently to avoid breaking user code
            pass  # Silent fail

    def flush(self):
        """
        Flush the log file.

        :param self: Instance of the Logger class.
        """

        try:  # Flush log file buffer
            self.logfile.flush()  # Flush log file
        except Exception:  # Fail silently
            pass  # Silent fail

    def close(self):
        """
        Close the log file.

        :param self: Instance of the Logger class.
        """

        try:  # Close log file
            self.logfile.close()  # Close log file
        except Exception:  # Fail silently
            pass  # Silent fail
