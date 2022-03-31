import os


def tlc_path():
    # For demo purposes, find the path to TLC in this repo, but you can use
    # a path to your own TLC jar.
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "large/tlc_2_18.jar")
    )


def apa_path():
    # For demo purposes, find the path to Apalache in this repo, but you can use
    # a path to your own Apalache jar.
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "large/apa_0_23_0.jar")
    )


def read_file(fn):
    # Utility used in these demos
    with open(os.path.join(os.path.dirname(__file__), fn), "r") as fd:
        return {fn: fd.read()}
