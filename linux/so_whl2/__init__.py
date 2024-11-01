"""SILK2 profile python module
"""
__all__ = []

try:
    import pyecharts
except ImportError:
    print('SILK2.Tools.profile requires "pyecharts" package.')
    print('Install it via command:')
    print('    pip3 install pyecharts')
    raise

try:
    import bs4
except ImportError:
    print('SILK2.Tools.profile requires "bs4" package.')
    print('Install it via command:')
    print('    pip3 install bs4')
    raise