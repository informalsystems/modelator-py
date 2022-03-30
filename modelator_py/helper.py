import logging
import os
import shutil
import typing

import pathos.multiprocessing as multiprocessing

LOG = logging.getLogger(__name__)


def get_filenames_in_dir(path):
    bases = os.listdir(path)
    full = [os.path.join(path, f) for f in bases]
    return [f for f in full if os.path.isfile(f)]


def get_dirnames_in_dir(path):
    bases = os.listdir(path)
    full = [os.path.join(path, f) for f in bases]
    return [f for f in full if os.path.isdir(f)]


def read_entire_dir_contents(path):
    """
    Read contents of directory into a dictionary

    Non recursive
    """
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


def parallel_map(function, data: typing.List):
    cores = multiprocessing.cpu_count()

    # Make chunk size smaller to fill up gaps
    # if processing time for different chunks differ
    HEURISTIC_PARAM = 2
    chunksize = len(data) // (cores * HEURISTIC_PARAM)

    with multiprocessing.ProcessPool(cores) as p:
        return p.map(function, data, chunksize=chunksize)
