"""
pyrtf-ng Errors and Exceptions
"""

class RTFError(Exception):
    pass


class ParseError(RTFError):
   """
   Unable to parse the RTF data.
   """
