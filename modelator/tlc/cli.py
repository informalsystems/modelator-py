import json

from .pure import tlc_pure
from .raw import RawCmd, TlcArgs, tlc_raw


class Tlc:
    def __init__(self, stdin):
        self.stdin = stdin

    def pure(self):
        assert self.stdin is not None
        data = json.loads(self.stdin.read())
        result = tlc_pure(json_obj=data)
        print(result)

    def raw(
        self,
        *,
        stdin=None,
        mem=False,
        cleanup=False,
        cwd=None,
        jar=None,
    ):
        process_result = None
        if stdin:
            data = json.loads(self.stdin.read())
            process_result = tlc_raw(json_obj=data)
        else:
            raw_cmd = RawCmd()
            raw_cmd.mem = mem
            raw_cmd.cleanup = cleanup
            raw_cmd.cwd = cwd
            raw_cmd.jar = jar
            raw_cmd.args = TlcArgs()
            process_result = tlc_raw(raw_cmd)

        stdout_pretty = process_result.stdout.decode("unicode_escape")
        stderr_pretty = process_result.stderr.decode("unicode_escape")

        print(
            f"""Ran 'tlc raw'.
shell cmd used: {process_result.args}
subprocess return code: {process_result.returncode}
stdout: {stdout_pretty}
stderr: {stderr_pretty}"""
        )
