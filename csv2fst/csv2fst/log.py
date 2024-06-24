"""Simple module for message logging during compilation (this might be
   replaced by a real logging library at some point)."""

from sys import stderr

# This is a temporary solution and should be replaced with proper logging

verbose=False
"""Ugly global variable toggles verbose mode for warnings"""

def set_verbose(mode):
    global verbose
    verbose = mode
    
def info(*msg, force=True):
    if force or verbose:
        print(*msg, file=stderr)

def warn(*msg, force=True):
    if force or verbose:
        print("\033[0;31m",end="",file=stderr)
        print(*msg, "\033[0m", file=stderr)
