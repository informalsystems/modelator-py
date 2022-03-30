import os
from pathlib import Path

TLC_PATH = "large/tlc_2_18.jar"
APALACHE_PATH = "large/apa_0_23_0.jar"


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
    return os.path.join(get_project_dir(), TLC_PATH)


def get_apalache_path():
    return os.path.join(get_project_dir(), APALACHE_PATH)
