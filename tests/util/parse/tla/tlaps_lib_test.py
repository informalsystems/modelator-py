"""Parse the files in the TLAPS library.

This module requires an installation of TLAPS.
"""
import os

from modelator.util.parse.tla import parser
from modelator.util.parse.tla import to_str


# change this variable to a path where
# the TLAPS library is present
TLAPS_LIB_PATH = "$HOME/lib/tlaps"


def parse_tlaps_modules():
    module_paths = _collect_tlaps_module_files()
    for module_path in module_paths:
        print(f"parsing module `{module_path}`")
        text = _read_file(module_path)
        _parse_and_format(text)


def _collect_tlaps_module_files():
    path = TLAPS_LIB_PATH
    path = os.path.expandvars(path)
    tlafiles = list()
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file() and entry.name.endswith(".tla"):
                tlafiles.append(entry)
    return [entry.path for entry in tlafiles]


def _read_file(path):
    with open(path, "r") as f:
        text = f.read()
    return text


def _parse_and_format(text):
    """Return parse tree from `tla.parser.parse`."""
    r = parser.parse(text, nodes=to_str.Nodes)
    assert r is not None
    text = r.to_str()
    to_str._print_overwide_lines(text, to_str.LINE_WIDTH)
    return r


if __name__ == "__main__":
    parse_tlaps_modules()
