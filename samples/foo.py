import sys

from modelator_py.apalache import apalache_pure, apalache_raw
from modelator_py.tlc import tlc_pure, tlc_raw
from modelator_py.util.tlc.itf import tlc_itf

# mypy: ignore-errors


def apalache_pure_demo():
    pass  # TODO:


def apalache_raw_demo():
    pass  # TODO:


def tlc_pure_demo():
    pass  # TODO:


def tlc_raw_demo():
    pass  # TODO:


def tlc_itf_demo():
    pass  # TODO:


if __name__ == "__main__":
    if sys.argv[1] == "apalache_pure":
        apalache_pure_demo()
    if sys.argv[1] == "apalache_raw":
        apalache_raw_demo()
    if sys.argv[1] == "tlc_pure":
        tlc_pure_demo()
    if sys.argv[1] == "tlc_raw":
        tlc_raw_demo()
    if sys.argv[1] == "tlc_itf_demo":
        tlc_itf_demo()
