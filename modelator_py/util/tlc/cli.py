import json as stdjson

from .itf import TlcITFCmd, tlc_itf


class Tlc:
    def __init__(self, stdin):
        self._stdin = stdin

    def itf(
        self,
        *,
        lists=True,
        records=True,
        json=False,  # Read parameters from Json?
    ):
        """
        Extract a list of Informal Trace Format traces from the stdout of TLC.

        Runs a parser over the contents of the stdout of a TLC execution to extract TLA+ traces
        and then converts them to Informal Trace Format.

        Arguments:
            lists : Convert 1-indexed functions (TLA+ sequences) to ITF lists?
            records : Convert string-indexed functions (TLA+ records) to ITF records?
            json : Read arguments from json instead of cli?
        """
        result = None
        if json:
            json_dict = stdjson.loads(self._stdin.read())
            result = tlc_itf(json=json_dict)
        else:

            assert (
                self._stdin is not None
            ), "TLC's stdout string should be passed on stdin if not passing json"

            cmd = TlcITFCmd()
            cmd.stdout = self._stdin.read()
            cmd.lists = lists
            cmd.records = records

            assert (
                cmd.stdout is not None
            ), "TLC's stdout string should be passed on stdin if not passing json"

            result = tlc_itf(cmd=cmd)

        obj_to_print = {}
        obj_to_print["traces"] = result

        to_print = stdjson.dumps(obj_to_print, indent=4, sort_keys=True)
        print(to_print)
