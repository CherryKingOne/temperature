import sys


def test_python_version() -> None:
    assert sys.version_info[:2] == (3, 12)


def test_pytest_available() -> None:
    import pytest

    assert pytest.__version__
