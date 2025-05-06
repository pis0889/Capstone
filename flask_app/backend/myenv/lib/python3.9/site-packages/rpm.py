"""Placeholder pending proper publication of RPM Python bindings"""
__version__ = "0.0.1"

import warnings

warning_msg = """\
The RPM Python bindings are not currently available via PyPI.

Please install them with your distro package manager (typically called
'python2-rpm' or 'python3-rpm'), and ensure that any virtual environments
needing the API are configured to be able to see the system site packages
directory.
"""

warnings.warn(warning_msg)