import os
from pathlib import Path

TLC_PATH = "/Users/danwt/Documents/work/modelator-py/mc_tlc.jar"
APALACHE_PATH = "/Users/danwt/Documents/work/modelator-py/mc_apa.jar"


def get_tests_dir():
    this_file_path = Path(__file__)
    return this_file_path.parent


def get_project_dir():
    tests_dir = get_tests_dir()
    return tests_dir.parent


def get_resource_dir():
    tests_dir = get_tests_dir()
    return os.path.join(tests_dir, "resource")


def get_tlc_path():
    return TLC_PATH


def get_apalache_path():
    return APALACHE_PATH
