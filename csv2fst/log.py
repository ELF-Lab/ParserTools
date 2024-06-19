"""Simple module for message logging during compilation (this might be
   replaced by a real logging library at some point)."""

from sys import stderr

# This is a temporary solution and should be replaced with proper logging

def info(*msg):
    print(*msg, file=stderr)

def warn(*msg):
    print(*msg, file=stderr)
