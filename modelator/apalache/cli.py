import json as stdjson

from .pure import apalache_pure
from .raw import ApalacheArgs, RawCmd, apalache_raw


class Apalache:
    def __init__(self, stdin, stdout):
        self._stdin = stdin
        self._stdout = stdout

    def pure(self):
        """
        Run Apalache without side effects using json input data.

        Runs Apalache in a temporary directory, writing all necessary data into the
        directory before calling Apalache, and reading back all necessary results
        back into memory.

        Writes the result to stdout in json.

        Requires json input data on stdin (`<command> < data.json`).
        """
        assert (
            self._stdin is not None
        ), "The pure interface requires json input in stdin"
        json_dict = stdjson.loads(self._stdin.read())

        result = apalache_pure(json=json_dict)
        to_print = stdjson.dumps(result, indent=4, sort_keys=True)
        print(to_print, file=self._stdout)

    def raw(
        self,
        *,
        json=None,
        mem=False,
        cleanup=False,
        cwd=None,
        jar=None,
    ):
        """
        Run Apalache without removing side effects (for debugging).

        Run Apalache directly without creating a temporary directory. This is mainly
        useful for debugging. Arguments can be provided on command line or by
        specifying the --json flag and providing json on stdin (`<command> < data.json`).

        Arguments:
            json : Read arguments from json instead of cli?
            mem : TODO:
            cleanup : TODO:
            cwd : Full path to directory to run Apalache from.
            jar : Full path to Apalache version 0.23.0 jar (other versions may work).
            TODO:

        """
        result = None
        if json:
            json_dict = stdjson.loads(self.stdin.read())
            result = apalache_raw(json_obj=json_dict)
        else:
            raw_cmd = RawCmd()
            raw_cmd.mem = mem
            raw_cmd.cleanup = cleanup
            raw_cmd.cwd = cwd
            raw_cmd.jar = jar
            raw_cmd.args = ApalacheArgs()

            result = apalache_raw(cmd=raw_cmd)

        stdout_pretty = result.process.stdout.decode("unicode_escape")
        stderr_pretty = result.process.stderr.decode("unicode_escape")

        obj_to_print = {}
        obj_to_print["shell_cmd"] = result.process.args
        obj_to_print["return_code"] = result.process.returncode
        obj_to_print["stdout"] = stdout_pretty
        obj_to_print["stderr"] = stderr_pretty
        obj_to_print["apalache_output_files"] = result.files

        to_print = stdjson.dumps(obj_to_print, indent=4, sort_keys=True)
        print(to_print, file=self._stdout)
