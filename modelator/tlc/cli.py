import json

from .pure import PureCmd, exec_tlc_pure_cmd
from .raw import TlcArgs, RawCmd, exec_tlc_raw_cmd


class Tlc:
    def __init__(self, stdin):
        self.stdin = stdin

    def raw(
        self,
        *,
        stdin=None,
        mem=False,
        cleanup=False,
        cwd=None,
        jar=None,
    ):
        cmd = None
        if stdin:
            data = json.loads(self.stdin.read())
            cmd = RawCmd()
            cmd.mem = data["mem"]
            cmd.cleanup = data["cleanup"]
            cmd.cwd = data["cwd"]
            cmd.jar = data["jar"]
            cmd.args = TlcArgs(**data["args"])

        else:
            cmd = RawCmd()
            cmd.mem = mem
            cmd.cleanup = cleanup
            cmd.cwd = cwd
            cmd.jar = jar
            cmd.args = TlcArgs()

        result = exec_tlc_raw_cmd(cmd)
        stdout_pretty = result.process.stdout.decode("unicode_escape")
        stderr_pretty = result.process.stderr.decode("unicode_escape")

        print(
            f"""Ran 'tlc raw'.
shell cmd: {result.process.args}
return code: {result.process.returncode}
files: {result.files}
stdout: {stdout_pretty}
stderr: {stderr_pretty}"""
        )

    def pure(self):
        assert self.stdin is not None
        data = json.loads(self.stdin.read())

        cmd = PureCmd()
        cmd.jar = data["jar"]
        cmd.args = TlcArgs(**data["args"])
        cmd.files = data["files"]

        result = exec_tlc_pure_cmd(cmd)

        """debug
        print(result["shell_cmd"])
        print(result["return_code"])
        print(result["stdout"])
        print(result["stderr"])
        print("\n".join(list(result["files"].keys())))
        for filename, file_content_str in result["files"].items():

            full_path = os.path.join(
                "/home/danwt/Documents/work/mbt-python/tempme", filename
            )
            with open(full_path, "w") as fd:
                fd.write(file_content_str)
        """

        print(result)
