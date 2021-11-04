import logging
import os
import shutil

LOG = logging.getLogger(__name__)


def get_filenames_in_dir(path):
    bases = os.listdir(path)
    full = [os.path.join(path, f) for f in bases]
    return [f for f in full if os.path.isfile(f)]


def read_entire_dir_contents(path):
    if not os.path.isabs(path):
        raise Exception(f"Cannot read directory {path=} as it is not absolute")
    files = get_filenames_in_dir(path)
    ret = {}
    for f in files:
        with open(f, "r") as fd:
            ret[f] = fd.read()
    return ret


def delete_dir(path):
    if not os.path.isabs(path):
        raise Exception(f"Cannot delete directory {path=} as it is not absolute")
    LOG.debug(f"Exec shutil.rmtree({path})")
    shutil.rmtree(path)
