"""How to parse a TLA+ module."""
from modelator_py.util.tla import parser
from modelator_py.util.tla.to_str import Nodes

TLA_FILE_PATH = "Counter.tla"


def parse_module():
    """Parse a TLA+ module."""
    tla_spec = _load_tla_module()
    tree = parser.parse(tla_spec)
    print(tree)


def parse_module_and_pretty_print():
    """Parse and print a TLA+ module."""
    tla_spec = _load_tla_module()
    tree = parser.parse(tla_spec, nodes=Nodes)
    s = tree.to_str(width=80)
    print(s)


def _load_tla_module():
    """Return contents of TLA+ file."""
    tla_file_path = TLA_FILE_PATH
    with open(tla_file_path, "r") as f:
        tla_spec = f.read()
    return tla_spec


if __name__ == "__main__":
    parse_module()
    parse_module_and_pretty_print()
