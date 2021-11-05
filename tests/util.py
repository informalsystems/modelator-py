import os
from pathlib import Path


def get_tests_dir():
    this_file_path = Path(__file__)
    return this_file_path.parent


def get_project_dir():
    tests_dir = get_tests_dir()
    return tests_dir.parent


def get_resource_dir():
    tests_dir = get_tests_dir()
    return os.path.join(tests_dir, "resource")


def get_apalache_path():
    project_dir = get_project_dir()
    apalache_jar = "apalache-pkg-0.17.1-full.jar"
    apalache_path = os.path.join(project_dir, apalache_jar)
    return apalache_path


def get_tlc_path():
    project_dir = get_project_dir()
    tlc_jar = "tla2tools.jar"
    tlc_path = os.path.join(project_dir, tlc_jar)
    return tlc_path
