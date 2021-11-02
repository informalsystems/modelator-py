from mbt_python import __version__


def test_version():
    assert __version__ == "0.1.0"


def test_multiply_two_numbers():
    result = 2 * 3
    assert result == 6
