import os

from modelator.tlc.pure import tlc_pure
from modelator.util.tlc.cli import tlc_itf
import json


def fn(s):
    root = "/Users/danwt/Documents/work/cosmos-sdk-fork/x/staking/mbt"
    return os.path.join(root, s)


def main():

    # get TLC stdout
    # split into trace strings
    # run genetic algorithm to split them